
import re
from pathlib import Path

from .utils import load_schema

SCHEMA = load_schema(Path('config/schema.yaml'))
COMPILED = {k: re.compile(v) for k, v in SCHEMA.get('patterns', {}).items()}

def validate_fields(text: str):
    results = {}
    for field in SCHEMA['required_fields']:
        pat = COMPILED.get(field)
        results[field] = bool(pat.search(text)) if pat else False
    return results
