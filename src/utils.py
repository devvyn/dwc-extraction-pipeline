from pathlib import Path
from typing import Dict, List

def load_schema(path: Path) -> Dict:
    data = {"required_fields": [], "patterns": {}}
    current = None
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        if line.endswith(':'):
            key = line[:-1].strip()
            current = key
            continue
        if line.startswith('- '):
            if current == 'required_fields':
                data['required_fields'].append(line[2:].strip())
            continue
        if current == 'patterns':
            if ':' in line:
                k, v = line.split(':', 1)
                k = k.strip()
                v = v.strip().strip("'").strip('"')
                v = v.encode().decode('unicode_escape')
                data['patterns'][k] = v
    return data
