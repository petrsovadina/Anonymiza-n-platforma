import re

def normalize_text(text: str) -> str:
    """Normalizuje text odstraněním nadbytečných mezer a převedením na malá písmena."""
    return re.sub(r'\s+', ' ', text).strip().lower()

def count_pii_entities(text: str, anonymized_text: str) -> int:
    """Spočítá počet anonymizovaných entit v textu."""
    return sum(1 for _ in re.finditer(r'<[A-Z_]+>', anonymized_text))
