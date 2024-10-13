from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

def anonymize_czech_text(text: str, analyzer: AnalyzerEngine) -> str:
    results = analyzer.analyze(text=text, language="cs")
    
    anonymizer = AnonymizerEngine()
    
    operators = {
        "PERSON": OperatorConfig("replace", {"new_value": "<OSOBA>"}),
        "EMAIL_ADDRESS": OperatorConfig("mask", {"chars_to_mask": 100, "masking_char": "*", "from_end": False}),
        "PHONE_NUMBER": OperatorConfig("mask", {"chars_to_mask": 100, "masking_char": "*", "from_end": False}),
        "DATE": OperatorConfig("replace", {"new_value": "<DATUM>"}),
        "LOCATION": OperatorConfig("replace", {"new_value": "<MÍSTO>"}),
        "RODNE_CISLO": OperatorConfig("mask", {"chars_to_mask": 100, "masking_char": "*", "from_end": False}),
        "CISLO_OP": OperatorConfig("mask", {"chars_to_mask": 100, "masking_char": "*", "from_end": False}),
        "CISLO_PASU": OperatorConfig("mask", {"chars_to_mask": 100, "masking_char": "*", "from_end": False}),
        "BANKOVNI_UCET": OperatorConfig("mask", {"chars_to_mask": 100, "masking_char": "*", "from_end": False}),
        "ADDRESS": OperatorConfig("replace", {"new_value": "<ADRESA>"}),
    }
    
    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results, operators=operators)
    
    return anonymized_result.text
