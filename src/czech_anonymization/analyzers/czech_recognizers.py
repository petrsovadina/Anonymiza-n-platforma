from presidio_analyzer import PatternRecognizer, Pattern
from .custom_recognizers import create_czech_custom_recognizers

def create_czech_recognizers():
    pattern_recognizers = [
        PatternRecognizer(
            supported_entity="RODNE_CISLO",
            patterns=[Pattern(name="rodne_cislo", regex=r"\b(\d{6}/\d{3,4})\b", score=0.8)],
            context=["rodné číslo", "r.č."]
        ),
        PatternRecognizer(
            supported_entity="CISLO_OP",
            patterns=[Pattern(name="cislo_op", regex=r"\b[A-Z]{2}\d{6}\b", score=0.8)],
            context=["občanský průkaz", "OP"]
        ),
        PatternRecognizer(
            supported_entity="CISLO_PASU",
            patterns=[Pattern(name="cislo_pasu", regex=r"\b[A-Z]\d{7}\b", score=0.8)],
            context=["cestovní pas", "pas"]
        ),
        PatternRecognizer(
            supported_entity="BANKOVNI_UCET",
            patterns=[Pattern(name="bankovni_ucet", regex=r"\b\d{1,6}-\d{1,10}/\d{4}\b", score=0.8)],
            context=["bankovní účet", "účet"]
        )
    ]
    
    custom_recognizers = create_czech_custom_recognizers()
    
    return pattern_recognizers + custom_recognizers
