import pytest
from src.main import create_analyzer
from czech_anonymization.processors.document_processors import anonymize_czech_text
from czech_anonymization.utils.text_utils import count_pii_entities

@pytest.fixture
def analyzer():
    return create_analyzer()

def test_anonymization(analyzer):
    text = "Jmenuji se Jan Novák, moje rodné číslo je 760305/3476 a můj email je jan.novak@example.com. Můžete mi zavolat na 123 456 789."
    anonymized = anonymize_czech_text(text, analyzer)
    
    assert "Jan Novák" not in anonymized
    assert "760305/3476" not in anonymized
    assert "jan.novak@example.com" not in anonymized
    assert "123 456 789" not in anonymized
    
    assert count_pii_entities(text, anonymized) == 4
