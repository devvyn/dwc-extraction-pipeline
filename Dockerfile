FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:${PATH}"

# System deps for Tesseract + OpenCV runtime (keeps later steps from whining)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tesseract-ocr tesseract-ocr-eng libtesseract-dev \
    libglib2.0-0 libgl1 build-essential pkg-config \
 && rm -rf /var/lib/apt/lists/*

# Install uv (Python package installer)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app

# 1) Put dependency manifests in the image
COPY pyproject.toml requirements.txt /app/

# 2) Install
RUN uv pip install --system -r /app/requirements.txt

# 3) Now copy the rest of the project
COPY . /app

CMD ["python", "src/main.py"]
