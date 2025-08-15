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
OCR output is saved to `output/ocr_texts/` with processing metadata in `output/status.csv`.
Extracted Darwin Core fields are written to `output/dwc_output/`.

Dependencies are declared in `pyproject.toml`. To export a pinned `requirements.txt` run:
```bash
uv pip compile pyproject.toml -o requirements.txt
```
