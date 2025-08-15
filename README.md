# Darwin Core OCR Pipeline Starter

## Overview
Extracts text from herbarium specimen sheets using local OCR (Tesseract) with fallback to OpenAI Vision.

## Setup

### Prerequisites
Install the [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) binary on your system before running the pipeline:

```bash
# macOS
brew install tesseract

# Debian/Ubuntu
sudo apt install tesseract-ocr

# Windows (Chocolatey)
choco install tesseract
```

### Install dependencies
```bash
cp .env.example .env
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
uv run python -m src.main
```

### Input and output
Place specimen images in the `input/` directory.
Preprocessed images are written to `output/preprocessed/`.
OCR output is saved to `output/ocr_texts/` with one JSON file per engine
(`*_tesseract.json`, `*_openai.json`). The file `output/status.csv` tracks
progress for each processing step (existence, preprocessing, each OCR method,
and field extraction) so runs are idempotent and resumable. To force redoing a
step, pass it via `--force`, e.g. `uv run python -m src.main --force openai`.
Extracted Darwin Core fields are written to `output/dwc_output/`.

Dependencies are declared in `pyproject.toml`. To export a pinned `requirements.txt` run:
```bash
uv pip compile pyproject.toml -o requirements.txt
```
