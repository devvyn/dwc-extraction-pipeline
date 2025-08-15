
import os, json
from pathlib import Path
import pandas as pd

from src.config import Config
from src.ocr_engine import run_tesseract
from src.openai_fallback import run_openai_vision
from src.image_preprocess import preprocess_image
from src.field_extractor import extract_fields
from src.validator import validate_fields

OCR_THRESHOLD = Config.OCR_THRESHOLD

INPUT_DIR = Path('input')
OUTPUT_DIR = Path('output/ocr_texts')
STATUS_FILE = Path('output/status.csv')

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)

if not STATUS_FILE.exists():
    pd.DataFrame(columns=['image_id', 'source', 'status', 'confidence']).to_csv(STATUS_FILE, index=False)

status_df = pd.read_csv(STATUS_FILE)
processed_ids = set(status_df['image_id'])

def save_status(df):
    df.to_csv(STATUS_FILE, index=False)

def process_image(img_path: Path):
    image_id = img_path.stem
    print(f'Processing {img_path.name} ...')

    temp_dir = Path('output/temp')
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_img = temp_dir / img_path.name
    try:
        preprocess_image(img_path, temp_img)
        pre_path = temp_img
    except Exception as e:
        print(f'Preprocess failed: {e}, using original.')
        pre_path = img_path

    result = run_tesseract(pre_path)
    result['source'] = 'tesseract'

    if result['confidence'] < OCR_THRESHOLD:
        print(f'Low confidence ({result["confidence"]:.2f}) → OpenAI Vision fallback.')
        oa_result = run_openai_vision(pre_path)
        if oa_result.get('text'):
            result = oa_result
        else:
            print('OpenAI Vision failed.')

    ocr_json = OUTPUT_DIR / f'{image_id}.json'
    with open(ocr_json, 'w') as f:
        json.dump(result, f, indent=2)

    dwc_fields = extract_fields(result['text'])
    dwc_out = Path('output/dwc_output') / f'{image_id}.json'
    dwc_out.parent.mkdir(parents=True, exist_ok=True)
    with open(dwc_out, 'w') as f:
        json.dump(dwc_fields, f, indent=2)

    is_valid = all(validate_fields(result['text']).values())
    status = 'success' if is_valid else 'needs_review'

    global status_df
    status_df = pd.concat([status_df, pd.DataFrame([{
        'image_id': image_id,
        'source': result.get('source'),
        'status': status,
        'confidence': result['confidence']
    }])], ignore_index=True)
    save_status(status_df)
    print(f'Done {img_path.name} — {status} (conf {result["confidence"]:.2f})')

def main():
    for img_file in INPUT_DIR.iterdir():
        if img_file.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
            continue
        if img_file.stem in processed_ids:
            print(f'Skipping {img_file.name}')
            continue
        try:
            process_image(img_file)
        except Exception as e:
            print(f'ERROR {img_file.name}: {e}')

if __name__ == '__main__':
    main()
