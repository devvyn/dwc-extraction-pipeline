
from src.field_extractor import extract_fields

def test_extract_fields():
    txt = """Achillea millefolium
    Date: 1982-07-23
    Collected by: Smith"""
    fields = extract_fields(txt)
    assert fields.get('scientificName') == 'Achillea millefolium'
