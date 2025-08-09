import re
from pathlib import Path

from .utils import load_schema

SCHEMA = load_schema(Path('config/schema.yaml'))

COMPILED = {k: re.compile(v) for k, v in SCHEMA.get('patterns', {}).items()}


def extract_fields(text: str):
    lines = [ln.strip() for ln in text.splitlines()]
    result = {}
    for field, pat in COMPILED.items():
        for line in lines:
            m = pat.search(line)
            if m:
                result[field] = m.group(1) if m.groups() else m.group(0)
                break
    return result
