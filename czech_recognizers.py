from typing import List
from presidio_analyzer import PatternRecognizer, Pattern

def create_czech_recognizers() -> List[PatternRecognizer]:
    recognizers = []

    # Rozpoznávač pro česká jména
    czech_name = PatternRecognizer(
        supported_entity="PERSON",
        patterns=[
            Pattern("Czech Name", r"\b[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+\s+[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+\b", 0.7)
        ],
        context=["jméno", "příjmení", "pan", "paní", "slečna"]
    )
    recognizers.append(czech_name)

    # Rozpoznávač pro české telefonní číslo
    czech_phone = PatternRecognizer(
        supported_entity="PHONE_NUMBER",
        patterns=[
            Pattern("Czech Phone", r"\b(\+420)?\s?[1-9]\d{2}\s?\d{3}\s?\d{3}\b", 0.75)
        ],
        context=["telefon", "mobil", "číslo"]
    )
    recognizers.append(czech_phone)

    # Rozpoznávač pro e-mailové adresy
    email_recognizer = PatternRecognizer(
        supported_entity="EMAIL",
        patterns=[
            Pattern("Email", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", 0.85)
        ],
        context=["email", "e-mail", "@"]
    )
    recognizers.append(email_recognizer)

    # Zde můžete přidat další české rozpoznávače podle potřeby

    return recognizers