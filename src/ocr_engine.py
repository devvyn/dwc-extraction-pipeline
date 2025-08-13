from pathlib import Path
from typing import Union

from PIL import Image

try:
    import pytesseract
    from pytesseract import Output
except ImportError:  # pragma: no cover - runtime check
    pytesseract = None
    Output = None


def run_tesseract(image_path: Union[str, Path]) -> dict:
    """Run Tesseract OCR on the given image.

    Parameters
    ----------
    image_path: Union[str, Path]
        Path to the image file to be processed.

    Returns
    -------
    dict
        A dictionary with extracted ``text`` and average ``confidence``.
    """
    if pytesseract is None:  # pragma: no cover - handled at runtime
        raise ImportError("pytesseract is required to use run_tesseract")

    with Image.open(image_path) as img:
        data = pytesseract.image_to_data(img, output_type=Output.DICT)

    words = [w for w in data.get('text', []) if w.strip()]
    text = " ".join(words)

    confs = [int(c) for c in data.get('conf', []) if c != '-1']
    confidence = sum(confs) / len(confs) / 100 if confs else 0.0

    return {"text": text, "confidence": confidence}
