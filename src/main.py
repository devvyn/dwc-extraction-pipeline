import argparse
import json
from pathlib import Path
import pandas as pd

from src.config import Config
from src.ocr_engine import run_tesseract
from src.openai_fallback import run_openai_vision
from src.image_preprocess import preprocess_image
from src.field_extractor import extract_fields
from src.validator import validate_fields

OCR_THRESHOLD = Config.OCR_THRESHOLD

INPUT_DIR = Path("input")
PRE_DIR = Path("output/preprocessed")
OCR_DIR = Path("output/ocr_texts")
DWC_DIR = Path("output/dwc_output")
STATUS_FILE = Path("output/status.csv")

PRE_DIR.mkdir(parents=True, exist_ok=True)
OCR_DIR.mkdir(parents=True, exist_ok=True)
DWC_DIR.mkdir(parents=True, exist_ok=True)
STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_status() -> pd.DataFrame:
    if STATUS_FILE.exists():
        return pd.read_csv(STATUS_FILE)
    df = pd.DataFrame(columns=["image_id", "step", "status", "confidence"])
    df.to_csv(STATUS_FILE, index=False)
    return df


status_df = _load_status()


def _save_status(df: pd.DataFrame) -> None:
    df.to_csv(STATUS_FILE, index=False)


def update_status(image_id: str, step: str, status: str, confidence: float | None = None) -> None:
    """Persist the status of a single processing step."""
    global status_df
    status_df = status_df[~((status_df["image_id"] == image_id) & (status_df["step"] == step))]
    status_df = pd.concat(
        [
            status_df,
            pd.DataFrame(
                [
                    {
                        "image_id": image_id,
                        "step": step,
                        "status": status,
                        "confidence": confidence,
                    }
                ]
            ),
        ],
        ignore_index=True,
    )
    _save_status(status_df)


def has_success(image_id: str, step: str) -> bool:
    return not status_df[
        (status_df["image_id"] == image_id)
        & (status_df["step"] == step)
        & (status_df["status"] == "success")
    ].empty


def _load_json(path: Path) -> dict | None:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def process_image(img_path: Path, force: set[str] | None = None) -> None:
    force = force or set()
    image_id = img_path.stem
    print(f"Processing {img_path.name} ...")

    update_status(image_id, "exists", "success")

    pre_path = PRE_DIR / img_path.name
    if "preprocess" in force or not has_success(image_id, "preprocess"):
        try:
            preprocess_image(img_path, pre_path)
            update_status(image_id, "preprocess", "success")
        except Exception:
            update_status(image_id, "preprocess", "failed")
            pre_path = img_path
    elif not pre_path.exists():
        # Status says success but file missing; redo to keep idempotent
        try:
            preprocess_image(img_path, pre_path)
            update_status(image_id, "preprocess", "success")
        except Exception:
            update_status(image_id, "preprocess", "failed")
            pre_path = img_path

    # Tesseract OCR
    tess_path = OCR_DIR / f"{image_id}_tesseract.json"
    if "tesseract" in force or not has_success(image_id, "ocr_tesseract"):
        try:
            t_result = run_tesseract(pre_path)
            t_result["source"] = "tesseract"
            with open(tess_path, "w") as f:
                json.dump(t_result, f, indent=2)
            update_status(image_id, "ocr_tesseract", "success", t_result["confidence"])
        except Exception:
            update_status(image_id, "ocr_tesseract", "failed")
            t_result = {}
    else:
        t_result = _load_json(tess_path) or {}

    # OpenAI OCR (optional)
    oa_result = None
    oa_path = OCR_DIR / f"{image_id}_openai.json"
    if Config.OPENAI_API_KEY:
        need_openai = (
            "openai" in force
            or (
                not has_success(image_id, "ocr_openai")
                and t_result.get("confidence", 0) < OCR_THRESHOLD
            )
        )
        if need_openai:
            try:
                oa_result = run_openai_vision(pre_path)
                with open(oa_path, "w") as f:
                    json.dump(oa_result, f, indent=2)
                update_status(
                    image_id, "ocr_openai", "success", oa_result.get("confidence")
                )
            except Exception:
                update_status(image_id, "ocr_openai", "failed")
        elif has_success(image_id, "ocr_openai"):
            oa_result = _load_json(oa_path)
        else:
            update_status(image_id, "ocr_openai", "skipped")
    else:
        update_status(image_id, "ocr_openai", "skipped")

    final_result = oa_result if oa_result else t_result

    # Field extraction
    dwc_out = DWC_DIR / f"{image_id}.json"
    if "extract" in force or not has_success(image_id, "extraction"):
        try:
            dwc_fields = extract_fields(final_result.get("text", ""))
            with open(dwc_out, "w") as f:
                json.dump(dwc_fields, f, indent=2)
            is_valid = all(validate_fields(final_result.get("text", "")).values())
            status = "success" if is_valid else "failed"
            update_status(image_id, "extraction", status, final_result.get("confidence"))
        except Exception:
            update_status(image_id, "extraction", "failed")

    print(f"Done {img_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        nargs="*",
        default=[],
        choices=["preprocess", "tesseract", "openai", "extract"],
        help="Redo specific steps even if marked successful",
    )
    args = parser.parse_args()
    force_steps = set(args.force)

    for img_file in INPUT_DIR.iterdir():
        if img_file.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            continue
        if not force_steps and has_success(img_file.stem, "extraction"):
            print(f"Skipping {img_file.name}")
            continue
        try:
            process_image(img_file, force_steps)
        except Exception as e:
            update_status(img_file.stem, "extraction", f"failed: {e}")
            print(f"ERROR {img_file.name}: {e}")


if __name__ == "__main__":
    main()

