import pytest
from PIL import Image
from unittest import mock

from src.image_preprocess import preprocess_image
from src.ocr_engine import run_tesseract


def test_preprocess_image(tmp_path, monkeypatch):
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    Image.new("RGB", (10, 10), "white").save(input_path)

    original_open = Image.open
    open_mock = mock.MagicMock(side_effect=original_open)
    monkeypatch.setattr("src.image_preprocess.Image.open", open_mock)

    original_save = Image.Image.save
    save_mock = mock.MagicMock()

    def save_stub(self, fp, *args, **kwargs):
        save_mock(fp)
        return original_save(self, fp, *args, **kwargs)

    monkeypatch.setattr(Image.Image, "save", save_stub)

    preprocess_image(input_path, output_path)

    open_mock.assert_called_once_with(input_path)
    save_mock.assert_called_once_with(output_path)

    assert output_path.exists()
    with Image.open(output_path) as img:
        assert img.mode == "L"


def test_run_tesseract(tmp_path, monkeypatch):
    img_path = tmp_path / "img.png"
    Image.new("RGB", (10, 10), "white").save(img_path)

    dummy_data = {
        "text": ["Hello", "World", ""],
        "conf": ["95", "80", "-1"],
    }

    def fake_image_to_data(image, output_type):
        assert output_type == DummyOutput.DICT
        return dummy_data

    class DummyOutput:
        DICT = "dict"

    fake_pytesseract = mock.MagicMock()
    fake_pytesseract.image_to_data = mock.MagicMock(side_effect=fake_image_to_data)

    monkeypatch.setattr("src.ocr_engine.pytesseract", fake_pytesseract)
    monkeypatch.setattr("src.ocr_engine.Output", DummyOutput)

    result = run_tesseract(img_path)
    assert result["text"] == "Hello World"
    assert result["confidence"] == pytest.approx((95 + 80) / 2 / 100)
    fake_pytesseract.image_to_data.assert_called_once()


def test_run_tesseract_import_error(monkeypatch):
    monkeypatch.setattr("src.ocr_engine.pytesseract", None)
    with pytest.raises(ImportError):
        run_tesseract("dummy.png")
