from pathlib import Path
from typing import Union

from PIL import Image, ImageOps, ImageFilter


def preprocess_image(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Convert the image to grayscale and enhance contrast.

    Parameters
    ----------
    input_path: Union[str, Path]
        Path to the original image file.
    output_path: Union[str, Path]
        Path where the preprocessed image will be saved.
    """
    with Image.open(input_path) as img:
        gray = ImageOps.grayscale(img)
        enhanced = ImageOps.autocontrast(gray)
        enhanced = enhanced.filter(ImageFilter.MedianFilter(size=3))
        enhanced.save(output_path)
