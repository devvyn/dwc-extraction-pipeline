# Darwin Core OCR Pipeline Starter

## Overview
Extracts text from herbarium specimen sheets using local OCR (Tesseract) with fallback to OpenAI Vision.

## Setup
```bash
cp .env.example .env
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
uv run python src/main.py
```

Dependencies are declared in `pyproject.toml`. To export a pinned `requirements.txt` run:
```bash
uv pip compile pyproject.toml -o requirements.txt
```
