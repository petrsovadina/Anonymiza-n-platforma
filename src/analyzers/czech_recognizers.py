from presidio_analyzer import PatternRecognizer

def create_czech_recognizers():
    recognizers = [
        PatternRecognizer(supported_language="cs", name="RODNE_CISLO", 
                          regex=r"\b(\d{6}/\d{3,4})\b", context=["rodné číslo", "r.č."]),
        PatternRecognizer(supported_language="cs", name="CISLO_OP", 
                          regex=r"\b[A-Z]{2}\d{6}\b", context=["občanský průkaz", "OP"]),
        PatternRecognizer(supported_language="cs", name="CISLO_PASU", 
                          regex=r"\b[A-Z]\d{7}\b", context=["cestovní pas", "pas"]),
        PatternRecognizer(supported_language="cs", name="BANKOVNI_UCET", 
                          regex=r"\b\d{1,6}-\d{1,10}/\d{4}\b", context=["bankovní účet", "účet"])
    ]
    return recognizers
