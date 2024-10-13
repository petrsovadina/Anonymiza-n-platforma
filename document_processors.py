from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

def anonymize_czech_text(text: str, analyzer: AnalyzerEngine, anonymization_method: str = "replace") -> str:
    # Analýza textu
    results = analyzer.analyze(text=text, language="cs")
    
    # Anonymizace
    anonymizer = AnonymizerEngine()
    
    # Nastavení metody anonymizace
    operators = {
        "PERSON": OperatorConfig(anonymization_method, {"new_value": "<OSOBA>"}),
        "EMAIL_ADDRESS": OperatorConfig(anonymization_method, {"new_value": "<EMAIL>"}),
        "PHONE_NUMBER": OperatorConfig(anonymization_method, {"new_value": "<TELEFON>"}),
        "RODNE_CISLO": OperatorConfig(anonymization_method, {"new_value": "<RODNÉ ČÍSLO>"}),
        "CISLO_OP": OperatorConfig(anonymization_method, {"new_value": "<ČÍSLO OP>"}),
        "CISLO_PASU": OperatorConfig(anonymization_method, {"new_value": "<ČÍSLO PASU>"}),
        "BANKOVNI_UCET": OperatorConfig(anonymization_method, {"new_value": "<BANKOVNÍ ÚČET>"}),
    }
    
    anonymized_text = anonymizer.anonymize(text=text, analyzer_results=results, operators=operators)
    
    return anonymized_text.text

# Použití
text = "Jmenuji se Jan Novák, moje rodné číslo je 760305/3476 a můj email je jan.novak@example.com. Můžete mi zavolat na 123 456 789. Číslo mého občanského průkazu je AB123456."
anonymized = anonymize_czech_text(text, analyzer)
print(anonymized)
