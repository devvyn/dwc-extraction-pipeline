from pathlib import Path

import src.main as m


REQUIRED_COLUMNS = ["image_id", "step", "status", "confidence"]


def run_load(tmp_path: Path, monkeypatch, contents: str):
    status_file = tmp_path / "status.csv"
    status_file.write_text(contents)
    monkeypatch.setattr(m, "STATUS_FILE", status_file)
    df = m._load_status()
    assert list(df.columns) == REQUIRED_COLUMNS
    # File should be rewritten with correct header
    assert status_file.read_text().splitlines()[0] == ",".join(REQUIRED_COLUMNS)


def test_load_status_with_empty_file(tmp_path, monkeypatch):
    run_load(tmp_path, monkeypatch, "")


def test_load_status_with_missing_columns(tmp_path, monkeypatch):
    run_load(tmp_path, monkeypatch, "image_id,status\nimg,success\n")
