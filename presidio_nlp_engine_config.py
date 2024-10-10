import logging
from typing import List, Tuple, Dict, Optional, Set
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
from presidio_analyzer import RecognizerRegistry, EntityRecognizer, RecognizerResult
from presidio_analyzer.predefined_recognizers import (
    CreditCardRecognizer, CryptoRecognizer, DateRecognizer, EmailRecognizer,
    IpRecognizer, PhoneRecognizer, UrlRecognizer, MedicalLicenseRecognizer
)
from presidio_analyzer.nlp_engine import NlpEngine, NlpArtifacts
from huggingface_hub import HfApi, HfFolder
import os
from czech_recognizers import create_czech_recognizers

logger = logging.getLogger("presidio-streamlit")

# Přidejte tuto definici na začátek souboru
TORCH_VERSION = torch.__version__

class TransformersNlpEngine(NlpEngine):
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.stopwords: Set[str] = set()
        logger.info(f"TransformersNlpEngine initialized with model: {model_path}")

    def _convert_tokens_to_text_positions(self, tokens, text):
        positions = []
        current_position = 0
        for token in tokens:
            if token.startswith("##"):
                positions.append(positions[-1])
            else:
                start = text.find(token, current_position)
                if start != -1:
                    positions.append(start)
                    current_position = start + len(token)
                else:
                    positions.append(current_position)
        return positions

    def process_text(self, text: str, language: str) -> NlpArtifacts:
        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            if TORCH_VERSION >= "1.9.0":
                predictions = torch.argmax(outputs.logits, dim=-1)[0]
            else:
                predictions = torch.argmax(outputs[0], dim=-1)[0]
            
            tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
            
            entities = []
            current_entity = None
            for i, (token, pred) in enumerate(zip(tokens, predictions)):
                if pred != 0:  # 0 je obvykle 'O' tag
                    entity_type = self.model.config.id2label[pred.item()]
                    if current_entity and current_entity[1] == entity_type:
                        current_entity[2] = i
                    else:
                        if current_entity:
                            entities.append(tuple(current_entity))
                        current_entity = [i, entity_type, i]
                else:
                    if current_entity:
                        entities.append(tuple(current_entity))
                        current_entity = None
            
            if current_entity:
                entities.append(tuple(current_entity))

            tokens_positions = self._convert_tokens_to_text_positions(tokens, text)

            logger.info(f"Processed text. Found {len(entities)} entities: {entities}")
            return NlpArtifacts(
                entities=entities,
                tokens=tokens,
                tokens_indices=tokens_positions,
                lemmas=tokens,  # Použijeme tokeny jako lemmy pro jednoduchost
                nlp_engine=self,
                language=language,
            )
        except Exception as e:
            logger.error(f"Error in process_text: {e}")
            raise

    def is_loaded(self) -> bool:
        return True

    def load(self) -> None:
        pass

    def process_batch(self, texts: List[str], language: Optional[str] = None) -> List[NlpArtifacts]:
        return [self.process_text(text, language or "cs") for text in texts]

    def is_stopword(self, word: str, language: str) -> bool:
        return word.lower() in self.stopwords

    def is_punct(self, token: str, language: str) -> bool:
        return all(not c.isalnum() for c in token)

    def get_supported_entities(self) -> List[str]:
        return list(set(self.model.config.id2label.values()))

    def get_supported_languages(self) -> List[str]:
        return ["cs", "en"]  # Podporujeme češtinu i angličtinu

class TransformersEntityRecognizer(EntityRecognizer):
    def __init__(
        self,
        supported_entities: List[str],
        name: str = "TransformersEntityRecognizer",
        supported_language: str = "cs",
    ):
        super().__init__(
            supported_entities=supported_entities,
            name=name,
            supported_language=supported_language,
        )
        logger.info(f"TransformersEntityRecognizer initialized with entities: {supported_entities}")

    def load(self) -> None:
        pass

    def analyze(self, text: str, entities: Optional[List[str]] = None, nlp_artifacts: NlpArtifacts = None) -> List[RecognizerResult]:
        results = []
        if not nlp_artifacts:
            logger.warning("No NlpArtifacts provided to TransformersEntityRecognizer")
            return results

        logger.info(f"Analyzing text with entities: {entities}")
        logger.info(f"NlpArtifacts entities: {nlp_artifacts.entities}")

        for start, entity_type, end in nlp_artifacts.entities:
            start_pos = nlp_artifacts.tokens_indices[start]
            end_pos = nlp_artifacts.tokens_indices[end] + len(nlp_artifacts.tokens[end])
            
            result = RecognizerResult(
                entity_type=entity_type,
                start=start_pos,
                end=end_pos,
                score=0.85,
                analysis_explanation=None
            )
            results.append(result)

        logger.info(f"Analyzed text. Found {len(results)} entities: {results}")
        return results

def create_transformer_engine(model_path: str) -> Tuple[NlpEngine, RecognizerRegistry]:
    nlp_engine = TransformersNlpEngine(model_path)
    if not nlp_engine.is_loaded():
        raise ValueError(f"Nepodařilo se načíst model z {model_path}")
    
    registry = RecognizerRegistry()
    supported_entities = nlp_engine.get_supported_entities()
    recognizer = TransformersEntityRecognizer(supported_entities=supported_entities)
    registry.add_recognizer(recognizer)
    
    # Přidání českých rozpoznávačů
    czech_recognizers = create_czech_recognizers()
    for czech_recognizer in czech_recognizers:
        registry.add_recognizer(czech_recognizer)
    
    logger.info(f"Registrované rozpoznávače: {[r.__class__.__name__ for r in registry.recognizers]}")
    
    return nlp_engine, registry

def create_piiranha_engine(model_name: str) -> Tuple[NlpEngine, RecognizerRegistry]:
    try:
        nlp_engine = TransformersNlpEngine(model_path=model_name)
        if not nlp_engine.is_loaded():
            raise ValueError(f"Failed to load model: {model_name}")
        registry = RecognizerRegistry()
        
        # Přidání TransformersEntityRecognizer pro češtinu a angličtinu
        registry.add_recognizer(TransformersEntityRecognizer(supported_entities=nlp_engine.get_supported_entities(), supported_language="cs"))
        registry.add_recognizer(TransformersEntityRecognizer(supported_entities=nlp_engine.get_supported_entities(), supported_language="en"))
        
        # Přidání předdefinovaných rozpoznávačů
        predefined_recognizers = [
            CreditCardRecognizer, CryptoRecognizer, DateRecognizer, EmailRecognizer,
            IpRecognizer, PhoneRecognizer, UrlRecognizer, MedicalLicenseRecognizer
        ]
        
        for recognizer_class in predefined_recognizers:
            registry.add_recognizer(recognizer_class(supported_language="cs"))
            registry.add_recognizer(recognizer_class(supported_language="en"))
        
        # Přidání českých rozpoznávačů
        czech_recognizers = create_czech_recognizers()
        for recognizer in czech_recognizers:
            registry.add_recognizer(recognizer)
        
        logger.info(f"Registered recognizers: {[r.__class__.__name__ for r in registry.recognizers]}")
        
        return nlp_engine, registry
    except Exception as e:
        logger.error(f"Error creating Piiranha engine: {e}")
        raise

def get_supported_entities(model_path: str) -> List[str]:
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    return list(set(model.config.id2label.values()))

def load_stopwords(language: str) -> Set[str]:
    return set()

def initialize_stopwords(nlp_engine: TransformersNlpEngine, language: str) -> None:
    nlp_engine.stopwords = load_stopwords(language)

def initialize_huggingface_auth():
    token = os.getenv("HUGGINGFACE_TOKEN")
    if token:
        HfFolder.save_token(token)
        # Nastavení tokenu pro API
        api = HfApi(token=token)
        logger.info("Hugging Face authentication initialized")
    else:
        logger.warning("HUGGINGFACE_TOKEN not found in environment variables")
