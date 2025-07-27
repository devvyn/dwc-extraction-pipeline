
import yaml

with open('config/schema.yaml') as f:
    SCHEMA = yaml.safe_load(f)

def validate_fields(text: str):
    results = {}
    for field in SCHEMA['required_fields']:
        results[field] = field in text
    return results
