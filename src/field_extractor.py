import re, yaml
from pathlib import Path

with open('config/schema.yaml') as f:
    SCHEMA = yaml.safe_load(f)

COMPILED = {k: re.compile(v) for k, v in SCHEMA.get('patterns', {}).items()}


def extract_fields(text: str):
    lines = text.splitlines()
    result = {}
    for field, pat in COMPILED.items():
        for line in lines:
            m = pat.search(line)
            if m:
                result[field] = m.group(0)
                break
    return result
