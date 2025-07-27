FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# System deps for Tesseract + OpenCV runtime (keeps later steps from whining)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-eng libtesseract-dev \
    libglib2.0-0 libgl1 build-essential pkg-config \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1) Put requirements in the image
COPY requirements.txt /app/requirements.txt

# 2) Install
RUN pip install --no-cache-dir -r /app/requirements.txt

# 3) Now copy the rest of the project
COPY . /app

CMD ["python", "src/main.py"]
