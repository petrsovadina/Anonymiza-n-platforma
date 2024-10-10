from typing import List, Optional, Tuple, Dict
import logging
import json
import csv
import io
from presidio_analyzer import AnalyzerEngine, RecognizerResult, PatternRecognizer, EntityRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer.nlp_engine import NlpEngine
from presidio_analyzer.recognizer_registry import RecognizerRegistry
from presidio_analyzer.predefined_recognizers import SpacyRecognizer
from czech_recognizers import create_czech_recognizers

from presidio_nlp_engine_config import create_transformer_engine, create_piiranha_engine
import re
import traceback

# Konfigurace logování
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Vypnutí logování pro některé moduly, které mohou být příliš upovídané
logging.getLogger("presidio_analyzer").setLevel(logging.WARNING)
logging.getLogger("presidio_anonymizer").setLevel(logging.WARNING)

logger = logging.getLogger("presidio-streamlit")

def get_nlp_engine_and_registry(model_name: str) -> Tuple[NlpEngine, RecognizerRegistry]:
    return create_transformer_engine(model_name)

def get_analyzer_engine(model_name: str) -> AnalyzerEngine:
    nlp_engine, registry = get_nlp_engine_and_registry(model_name)
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=registry)
    
    # Přidání českých rozpoznávačů
    czech_recognizers = create_czech_recognizers()
    for recognizer in czech_recognizers:
        analyzer.registry.add_recognizer(recognizer)
    
    return analyzer

def get_anonymizer_engine():
    return AnonymizerEngine()

def get_supported_entities(model_name: str):
    analyzer = get_analyzer_engine(model_name)
    entities = analyzer.get_supported_entities()
    # Přidání nových českých entit a entit rozpoznávaných modelem Piiranha do seznamu
    additional_entities = [
        "CZECH_ID", "CZECH_BIRTH_NUMBER", "CZECH_PHONE", "CZECH_ADDRESS",
        "CZECH_BANK_ACCOUNT", "CZECH_PASSPORT", "CZECH_DRIVING_LICENSE",
        "CZECH_ICO", "CZECH_DIC", "CZECH_SIPO", "CZECH_DATA_BOX",
        "I-CITY", "I-EMAIL", "I-PERSON", "I-PHONE", "I-ORG", "I-LOC", "I-CRYPTO",
        "I-IP", "I-CREDIT_CARD", "I-NRP", "I-MEDICAL_LICENSE", "I-DATE", "I-URL"
    ]
    entities.extend(additional_entities)
    return list(set(entities))  # Odstranění případných duplikt

def analyze_text(model_name: str, text: str, entities: Optional[List[str]] = None, threshold: float = 0.5, language: str = "cs"):
    logger.info(f"Analyzuji text s modelem: {model_name}, jazyk: {language}, entity: {entities}")
    analyzer = get_analyzer_engine(model_name)
    
    try:
        entities_list = [str(entity) for entity in entities] if entities else None
        
        analysis_results = analyzer.analyze(
            text=text,
            language=language,
            entities=entities_list,
            score_threshold=threshold
        )
        
        logger.info(f"Detekované entity: {analysis_results}")
        
        return [result for result in analysis_results if result.start < len(text) and result.end <= len(text)]
    except Exception as e:
        logger.error(f"Chyba při analýze textu: {e}")
        raise

def calculate_anonymization_accuracy(original_text: str, anonymized_text: str, analyze_results: List[RecognizerResult]) -> float:
    total_pii = len(analyze_results)
    correctly_anonymized = sum(1 for r in analyze_results if anonymized_text[r.start:r.end] != original_text[r.start:r.end])
    return correctly_anonymized / total_pii if total_pii > 0 else 1.0

def get_custom_operator_config(entity_type: str, anonymization_method: str) -> Dict[str, OperatorConfig]:
    operators = {}
    
    if anonymization_method == "mask":
        operators[entity_type] = OperatorConfig("mask", {"chars_to_mask": 4, "masking_char": "*", "from_end": True})
    elif anonymization_method == "replace":
        operators[entity_type] = OperatorConfig("replace", {"new_value": f"[{entity_type}]"})
    elif anonymization_method == "redact":
        operators[entity_type] = OperatorConfig("redact", {})
    elif anonymization_method == "hash":
        operators[entity_type] = OperatorConfig("hash", {"hash_type": "md5"})
    else:
        operators[entity_type] = OperatorConfig("replace", {"new_value": "[REDACTED]"})
    
    return operators

def anonymize_text(
    text: str,
    operator: str,
    analyze_results: List[RecognizerResult],
    mask_char: Optional[str] = None,
    chars_to_mask: Optional[int] = None,
):
    anonymizer = get_anonymizer_engine()
    
    # Převod českých názvů operátorů na anglické
    operator_mapping = {
        "odstranění": "replace",
        "nahrazení": "replace",
        "maskování": "mask",
        "hashování": "hash"
    }
    operator = operator_mapping.get(operator.lower(), operator.lower())
    
    if operator == "mask":
        operator_config = {
            "type": "mask",
            "masking_char": mask_char or "*",
            "chars_to_mask": chars_to_mask or 0,  # 0 znamená maskovat vše
            "from_end": False,
        }
    elif operator == "replace":
        operator_config = {"type": "replace", "new_value": "[REDACTED]"}
    elif operator == "hash":
        operator_config = {"type": "hash", "hash_type": "md5"}
    else:
        raise ValueError(f"Nepodporovaný operátor anonymizace: {operator}")

    result = anonymizer.anonymize(
        text,
        analyze_results,
        operators={"DEFAULT": OperatorConfig(operator, operator_config)},
    )
    return result.text

def highlight_pii(text: str, analyze_results: List[RecognizerResult]) -> str:
    """Zvýrazní detekované PII v textu."""
    highlighted_text = text
    for result in sorted(analyze_results, key=lambda x: x.start, reverse=True):
        highlighted_text = (
            highlighted_text[:result.start]
            + f"<span style='background-color: yellow;' title='{result.entity_type}'>{highlighted_text[result.start:result.end]}</span>"
            + highlighted_text[result.end:]
        )
    return highlighted_text

def export_results(anonymized_text: str, analyze_results: List[RecognizerResult], format: str) -> str:
    """Exportuje výsledky anonymizace v různých formátech."""
    if format == "txt":
        return anonymized_text
    elif format == "json":
        return json.dumps({
            "anonymized_text": anonymized_text,
            "detected_pii": [{"entity_type": r.entity_type, "start": r.start, "end": r.end, "score": r.score} for r in analyze_results]
        }, ensure_ascii=False)
    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Entity Type", "Start", "End", "Score", "Anonymized Value"])
        for r in analyze_results:
            writer.writerow([r.entity_type, r.start, r.end, r.score, anonymized_text[r.start:r.end]])
        return output.getvalue()
    else:
        raise ValueError(f"Nepodporovaný formát exportu: {format}")

def annotate_text(text: str, analyze_results: List[RecognizerResult]):
    tokens = []
    results = anonymize_text(text=text, operator="replace", analyze_results=analyze_results)
    results = sorted(results.items, key=lambda x: x.start)
    
    for i, res in enumerate(results):
        if i == 0:
            tokens.append(text[: res.start])
        tokens.append((text[res.start : res.end], res.entity_type))
        if i != len(results) - 1:
            tokens.append(text[res.end : results[i + 1].start])
        else:
            tokens.append(text[res.end :])
    return tokens