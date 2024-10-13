from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from utils.config import ANONYMIZATION_MAPPING, DEFAULT_LANGUAGE

def anonymize_czech_text(text: str, analyzer: AnalyzerEngine, anonymization_method: str = "replace") -> str:
    results = analyzer.analyze(text=text, language=DEFAULT_LANGUAGE)
    
    anonymizer = AnonymizerEngine()
    
    operators = {
        entity_type: OperatorConfig(anonymization_method, {"new_value": new_value})
        for entity_type, new_value in ANONYMIZATION_MAPPING.items()
    }
    
    anonymized_text = anonymizer.anonymize(text=text, analyzer_results=results, operators=operators)
    
    return anonymized_text.text
