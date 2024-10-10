import streamlit as st
import pandas as pd
from typing import List, Dict
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from dotenv import load_dotenv
import os

from presidio_nlp_engine_config import (
    create_transformer_engine,
    create_piiranha_engine,
    get_supported_entities,
    initialize_huggingface_auth
)

from presidio_helpers import (
    get_analyzer_engine,
    get_anonymizer_engine,
    analyze_text,
    anonymize_text
)

from czech_recognizers import create_czech_recognizers

# Načtení proměnných prostředí
load_dotenv()

# Inicializace Hugging Face autentizace
initialize_huggingface_auth()

# Nastavení stránky
st.set_page_config(page_title="Czech PII Anonymizer", layout="wide")

# Sidebar
st.sidebar.title("Nastavení anonymizace")

# Výběr modelu
model_options = {
    "Piiranha": "iiiorg/piiranha-v1-detect-personal-information",
    "Vlastní model": os.getenv("CUSTOM_MODEL_PATH", "cesta/k/vašemu/modelu"),
}
selected_model = st.sidebar.selectbox("Vyberte model", list(model_options.keys()))

# Metoda anonymizace
anon_method_mapping = {
    "Nahrazení": "replace",
    "Maskování": "mask",
    "Odstranění": "redact",
    "Hashování": "hash"
}
anon_method_cs = st.sidebar.selectbox(
    "Metoda anonymizace",
    list(anon_method_mapping.keys()),
    help="Vyberte způsob anonymizace detekovaných PII."
)
anon_method = anon_method_mapping[anon_method_cs]

# Agregovaná redakce
aggregate_redaction = st.sidebar.checkbox("Agregovaná redakce", value=True, 
                                          help="Pokud je zaškrtnuto, všechny PII budou označeny jako '[redacted]'. Jinak budou označeny specifickým typem PII.")

# PII kategorie
@st.cache_data
def get_all_supported_entities(model_path: str):
    model_entities = get_supported_entities(model_path)
    czech_entities = [recognizer.supported_entities[0] for recognizer in create_czech_recognizers()]
    return list(set(model_entities + czech_entities))

pii_categories = get_all_supported_entities(model_options[selected_model])
selected_categories = st.sidebar.multiselect(
    "PII kategorie k anonymizaci",
    pii_categories,
    default=list(pii_categories)[:3],
    help="Vyberte typy PII, které chcete anonymizovat."
)

# Hlavní obsah
st.title("Komplexní anonymizační platforma pro české texty")

# Vstupní sekce
st.header("Vstupní text")
input_method = st.radio("Vyberte metodu vstupu:", ("Nahrát soubor", "Vložit text"))

if input_method == "Nahrát soubor":
    uploaded_file = st.file_uploader("Nahrajte soubor (TXT, PDF, DOCX):", type=["txt", "pdf", "docx"])
    if uploaded_file:
        try:
            from document_processors import read_file_content
            input_text = read_file_content(uploaded_file, uploaded_file.type)
        except Exception as e:
            st.error(f"Chyba při čtení souboru: {e}")
            input_text = ""
else:
    input_text = st.text_area("Vložte text k anonymizaci:", height=200)

# Mapování entit pro zobrazení
entity_mapping = {
    "PERSON": "Osoba",
    "PHONE_NUMBER": "Telefonní číslo",
    "EMAIL": "E-mail",
    "ADDRESS": "Adresa",
    "CREDIT_CARD": "Kreditní karta",
    "IBAN_CODE": "IBAN",
    "ID": "Identifikační číslo",
    "IP_ADDRESS": "IP adresa",
    # Přidejte další mapování podle potřeby
}

# Proces anonymizace
if st.button("Anonymizovat"):
    if input_text:
        try:
            # Analýza textu
            with st.spinner('Analyzuji text...'):
                results = analyze_text(model_options[selected_model], input_text, selected_categories)
            
            # Zobrazení detekovaných entit pro diagnostiku
            st.write("Detekované entity:")
            for result in results:
                entity_type = entity_mapping.get(result.entity_type, result.entity_type)
                st.write(f"{entity_type}: {input_text[result.start:result.end]}")
            
            # Anonymizace textu
            with st.spinner('Anonymizuji text...'):
                anonymized_text = anonymize_text(
                    text=input_text,
                    operator=anon_method,
                    analyze_results=results,
                    mask_char='*' if anon_method == "mask" else None,
                    chars_to_mask=0 if anon_method == "mask" else None
                )

            # Zobrazení výsledků
            st.header("Výsledky anonymizace")
            st.text_area("Anonymizovaný text:", value=anonymized_text, height=200)

            # Možnosti exportu
            st.header("Export výsledků")
            st.download_button("Stáhnout anonymizovaný text", anonymized_text, "anonymized_text.txt")

            # Přidání do historie
            if 'history' not in st.session_state:
                st.session_state.history = []
            
            st.session_state.history.append({
                "Model": selected_model,
                "Metoda anonymizace": anon_method_cs,
                "Počet detekovaných PII": len(results),
                "Délka vstupního textu": len(input_text),
                "Délka výstupního textu": len(anonymized_text)
            })
        except Exception as e:
            st.error(f"Došlo k chybě při zpracování textu: {e}")
            st.info("Prosím, zkontrolujte své internetové připojení a zkuste to znovu.")

# Historie anonymizací
st.header("Historie anonymizací")
if 'history' in st.session_state and st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history)
    st.dataframe(history_df)
else:
    st.info("Zatím nebyla provedena žádná anonymizace.")

# Nápověda a dokumentace
st.header("Nápověda a dokumentace")
with st.expander("Jak používat Czech PII Anonymizer"):
    st.write("""
    1. Vyberte NER model v postranním panelu.
    2. Zvolte metodu anonymizace.
    3. Vyberte kategorie PII, které chcete anonymizovat.
    4. Nahrajte soubor nebo vložte text k anonymizaci.
    5. Klikněte na tlačítko 'Anonymizovat'.
    6. Prohlédněte si výsledky a stáhněte anonymizovaný text.
    7. Historie anonymizací je k dispozici ve spodní části stránky.
    """)

# Footer
st.markdown("---")
st.markdown("© 2023 Czech PII Anonymizer. Všechna práva vyhrazena.")