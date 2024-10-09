import logging
from typing import List, Tuple, Dict, Optional, Set
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
from presidio_analyzer import RecognizerRegistry, EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngine, NlpArtifacts
from huggingface_hub import HfApi, HfFolder
import os

logger = logging.getLogger("presidio-streamlit")

class TransformersNlpEngine(NlpEngine):
    def __init__(self, model_path: str):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForTokenClassification.from_pretrained(model_path)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            self.is_loaded_flag = True
            self.stopwords = set()  # Initialize an empty set of stopwords
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.is_loaded_flag = False

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
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        predictions = torch.argmax(outputs.logits, dim=-1)[0]
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        
        entities = []
        for i, (token, pred) in enumerate(zip(tokens, predictions)):
            if pred != 0:  # 0 is usually the 'O' tag
                entity_type = self.model.config.id2label[pred.item()]
                entities.append((i, entity_type))

        tokens_positions = self._convert_tokens_to_text_positions(tokens, text)

        return NlpArtifacts(
            entities=entities,
            tokens=tokens,
            tokens_indices=tokens_positions,
            lemmas=tokens,  # Using tokens as lemmas for simplicity
            nlp_engine=self,
            language=language,
        )

    def is_loaded(self) -> bool:
        return self.is_loaded_flag

    def load(self) -> None:
        self.is_loaded_flag = True

    def process_batch(self, texts: List[str], language: Optional[str] = None) -> List[NlpArtifacts]:
        return [self.process_text(text, language or "cs") for text in texts]

    def is_stopword(self, word: str, language: str) -> bool:
        return word.lower() in self.stopwords

    def is_punct(self, token: str, language: str) -> bool:
        # Ignore the language parameter as our implementation is language-independent
        return all(not c.isalnum() for c in token)

    def get_supported_entities(self) -> List[str]:
        return list(set(self.model.config.id2label.values()))

    def get_supported_languages(self) -> List[str]:
        return ["cs"]  # Assuming only Czech is supported

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

    def load(self) -> None:
        pass

    def analyze(self, text: str, entities: Optional[List[str]] = None, nlp_artifacts: NlpArtifacts = None) -> List[RecognizerResult]:
        results = []
        if not nlp_artifacts:
            return results

        for idx, (start, entity_type) in enumerate(nlp_artifacts.entities):
            if entities and entity_type not in entities:
                continue
            end = idx + 1
            while end < len(nlp_artifacts.entities) and nlp_artifacts.entities[end][1] == entity_type:
                end += 1
            
            start_pos = nlp_artifacts.tokens_indices[start]
            end_pos = nlp_artifacts.tokens_indices[end - 1] + len(nlp_artifacts.tokens[end - 1])
            
            result = RecognizerResult(
                entity_type=entity_type,
                start=start_pos,
                end=end_pos,
                score=0.85,  # You might want to adjust this or use model confidence
                analysis_explanation=None
            )
            results.append(result)

        return results

def create_transformer_engine(model_path: str) -> Tuple[NlpEngine, RecognizerRegistry]:
    nlp_engine = TransformersNlpEngine(model_path)
    if not nlp_engine.is_loaded():
        raise ValueError(f"Failed to load model from {model_path}")
    
    registry = RecognizerRegistry()
    supported_entities = nlp_engine.get_supported_entities()
    recognizer = TransformersEntityRecognizer(supported_entities=supported_entities)
    registry.add_recognizer(recognizer)
    
    return nlp_engine, registry

# Piiranha uses the same TransformersNlpEngine
def create_piiranha_engine(model_name: str) -> Tuple[NlpEngine, RecognizerRegistry]:
    try:
        nlp_engine = TransformersNlpEngine(model_path=model_name)
        if not nlp_engine.is_loaded:
            raise ValueError(f"Failed to load model: {model_name}")
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers()
        return nlp_engine, registry
    except Exception as e:
        logger.error(f"Error creating Piiranha engine: {e}")
        raise

# Function to get supported entities for a given model
def get_supported_entities(model_path: str) -> List[str]:
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    return list(set(model.config.id2label.values()))

# Helper function to load stopwords if needed
def load_stopwords(language: str) -> Set[str]:
    # Implement loading of stopwords for the given language
    # This is just a placeholder, you should implement actual loading of stopwords
    return set()

# Initialize stopwords
def initialize_stopwords(nlp_engine: TransformersNlpEngine, language: str) -> None:
    nlp_engine.stopwords = load_stopwords(language)

def initialize_huggingface_auth():
    token = os.environ.get("HUGGINGFACE_TOKEN")
    if token:
        HfFolder.save_token(token)
        api = HfApi(token=token)
    else:
        logger.warning("HUGGINGFACE_TOKEN not found in environment variables")