
import pytesseract
from PIL import Image

def run_tesseract(image_path):
    img = Image.open(image_path)
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    confidences = [int(c) for c in ocr_data['conf'] if c.isdigit() and int(c) > 0]
    confidence = sum(confidences)/len(confidences) if confidences else 0
    text = "\n".join(ocr_data['text'])
    return {'text': text.strip(), 'confidence': confidence}
