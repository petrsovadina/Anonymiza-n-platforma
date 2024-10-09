from typing import List, Optional, Tuple, Dict
import logging
import streamlit as st
import json
import csv
import io
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer.nlp_engine import NlpEngine
from presidio_analyzer import RecognizerRegistry

from presidio_nlp_engine_config import create_transformer_engine, create_piiranha_engine

logger = logging.getLogger("presidio-streamlit")

@st.cache_resource
def get_nlp_engine_and_registry(model_name: str) -> Tuple[NlpEngine, RecognizerRegistry]:
    try:
        if "piiranha" in model_name.lower():
            return create_piiranha_engine(model_name)
        else:
            return create_transformer_engine(model_name)
    except Exception as e:
        logger.error(f"Error creating NLP engine: {e}")
        raise

@st.cache_resource
def get_analyzer_engine(model_name: str) -> AnalyzerEngine:
    try:
        nlp_engine, registry = get_nlp_engine_and_registry(model_name)
        analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=registry)
        return analyzer
    except Exception as e:
        logger.error(f"Error creating analyzer engine: {e}")
        raise

@st.cache_resource
def get_anonymizer_engine():
    return AnonymizerEngine()

@st.cache_data
def get_supported_entities(model_name: str):
    analyzer = get_analyzer_engine(model_name)
    return analyzer.get_supported_entities()

def analyze_text(model_name: str, text: str, entities: Optional[List[str]] = None, threshold: float = 0.5, language: str = "cs"):
    analyzer = get_analyzer_engine(model_name)
    results = analyzer.analyze(text=text, entities=entities, language=language, score_threshold=threshold)
    return [result for result in results if result.start < len(text) and result.end <= len(text)]

def calculate_anonymization_accuracy(original_text: str, anonymized_text: str, analyze_results: List[RecognizerResult]) -> float:
    total_pii = len(analyze_results)
    correctly_anonymized = sum(1 for r in analyze_results if anonymized_text[r.start:r.end] != original_text[r.start:r.end])
    return correctly_anonymized / total_pii if total_pii > 0 else 1.0

def anonymize_text(
    text: str,
    operator: str,
    analyze_results: List[RecognizerResult],
    mask_char: Optional[str] = None,
    chars_to_mask: Optional[int] = None,
    entity_operators: Optional[Dict[str, str]] = None
):
    anonymizer = get_anonymizer_engine()
    
    def get_operator_config(op: str):
        if op == "mask":
            return {
                "type": "mask",
                "masking_char": mask_char,
                "chars_to_mask": chars_to_mask,
                "from_end": False,
            }
        elif op == "remove":
            return {"type": "replace", "new_value": ""}
        elif op == "replace":
            return {"type": "replace", "new_value": "[REDACTED]"}
        else:
            return None
    
    operators = {"DEFAULT": OperatorConfig(operator, get_operator_config(operator))}
    
    if entity_operators:
        for entity, op in entity_operators.items():
            operators[entity] = OperatorConfig(op, get_operator_config(op))
    
    result = anonymizer.anonymize(
        text,
        analyze_results,
        operators=operators,
    )
    return result

def highlight_pii(text: str, analyze_results: List[RecognizerResult]) -> str:
    highlighted_text = text
    for result in sorted(analyze_results, key=lambda x: x.start, reverse=True):
        if result.start < len(text) and result.end <= len(text):
            highlighted_text = (
                highlighted_text[:result.start]
                + f"<span style='background-color: yellow;' title='{result.entity_type}'>{highlighted_text[result.start:result.end]}</span>"
                + highlighted_text[result.end:]
            )
    return highlighted_text

def export_results(anonymized_text: str, analyze_results: List[RecognizerResult], format: str) -> str:
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