from typing import Dict

ANONYMIZATION_MAPPING: Dict[str, str] = {
    "PERSON": "<OSOBA>",
    "EMAIL_ADDRESS": "<EMAIL>",
    "PHONE_NUMBER": "<TELEFON>",
    "RODNE_CISLO": "<RODNÉ ČÍSLO>",
    "CISLO_OP": "<ČÍSLO OP>",
    "CISLO_PASU": "<ČÍSLO PASU>",
    "BANKOVNI_UCET": "<BANKOVNÍ ÚČET>",
}

DEFAULT_LANGUAGE = "cs"
