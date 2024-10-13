import spacy
import streamlit as st
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.predefined_recognizers import EmailRecognizer, PhoneRecognizer
from czech_anonymization.analyzers.czech_recognizers import create_czech_recognizers
from czech_anonymization.processors.document_processors import anonymize_czech_text

def create_analyzer():
    # Načtení vícejazyčného modelu spaCy
    nlp = spacy.load("xx_ent_wiki_sm")

    # Vytvoření NLP enginu s načteným modelem
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "cs", "model_name": "xx_ent_wiki_sm"}]
    }
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    # Nastavení českých rozpoznávačů
    registry = RecognizerRegistry()
    registry.add_recognizer(EmailRecognizer(supported_language="cs"))
    registry.add_recognizer(PhoneRecognizer(supported_language="cs"))

    # Přidání dalších českých rozpoznávačů včetně vlastních
    for recognizer in create_czech_recognizers():
        registry.add_recognizer(recognizer)

    return AnalyzerEngine(
        registry=registry,
        nlp_engine=nlp_engine,
        supported_languages=["cs"]
    )

def main():
    st.title("Česká Anonymizační Platforma")

    analyzer = create_analyzer()

    text = st.text_area("Zadejte text k anonymizaci:", height=200)
    
    if st.button("Anonymizovat"):
        if text:
            anonymized = anonymize_czech_text(text, analyzer)
            st.subheader("Anonymizovaný text:")
            st.write(anonymized)
        else:
            st.warning("Prosím, zadejte text k anonymizaci.")

if __name__ == "__main__":
    main()
