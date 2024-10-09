import streamlit as st
import pandas as pd
from typing import List, Dict
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import io
from PyPDF2 import PdfReader
from docx import Document
import re
import json
import csv

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

def read_file_content(uploaded_file):
    file_type = uploaded_file.type
    if file_type == "text/plain":
        return uploaded_file.getvalue().decode("utf-8")
    elif file_type == "application/pdf":
        pdf_reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
        return "\n".join(page.extract_text() for page in pdf_reader.pages)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(io.BytesIO(uploaded_file.getvalue()))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    else:
        raise ValueError(f"Nepodporovaný typ souboru: {file_type}")

def highlight_pii(text, results):
    highlighted_text = text
    for result in sorted(results, key=lambda x: x.start, reverse=True):
        highlighted_text = (
            highlighted_text[:result.start]
            + f"<span style='background-color: yellow;'>{highlighted_text[result.start:result.end]}</span>"
            + highlighted_text[result.end:]
        )
    return highlighted_text

def export_results(anonymized_text, results, format):
    if format == "txt":
        return anonymized_text
    elif format == "json":
        return json.dumps({
            "anonymized_text": anonymized_text,
            "detected_pii": [{"entity_type": r.entity_type, "start": r.start, "end": r.end} for r in results]
        }, ensure_ascii=False)
    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Entity Type", "Start", "End", "Anonymized Value"])
        for r in results:
            writer.writerow([r.entity_type, r.start, r.end, anonymized_text[r.start:r.end]])
        return output.getvalue()

# Inicializace Hugging Face autentizace
initialize_huggingface_auth()

# Nastavení stránky
st.set_page_config(page_title="Czech PII Anonymizer", layout="wide")

# Sidebar
st.sidebar.title("Nastavení anonymizace")

# Výběr modelu
model_options = {
    "Piiranha": "iiiorg/piiranha-v1-detect-personal-information",
    "Vlastní model": "cesta/k/vašemu/modelu",  # Nahraďte skutečnou cestou k vašemu modelu
}
selected_model = st.sidebar.selectbox("Vyberte model", list(model_options.keys()))

# Metoda anonymizace
anon_method = st.sidebar.selectbox(
    "Metoda anonymizace",
    ["Odstranění", "Nahrazení", "Maskování"],
    help="Vyberte způsob anonymizace detekovaných PII."
)

# Agregovaná redakce
aggregate_redaction = st.sidebar.checkbox("Agregovaná redakce", value=True, 
                                          help="Pokud je zaškrtnuto, všechny PII budou označeny jako '[redacted]'. Jinak budou označeny specifickým typem PII.")

# PII kategorie
pii_categories = get_supported_entities(model_options[selected_model])
selected_categories = st.sidebar.multiselect(
    "PII kategorie k anonymizaci",
    pii_categories,
    default=list(pii_categories)[:3],
    help="Vyberte typy PII, které chcete anonymizovat."
)

# Pokročilá nastavení
with st.sidebar.expander("Pokročilá nastavení"):
    threshold = st.slider("Práh detekce", 0.0, 1.0, 0.5, help="Minimální skóre pro detekci PII")
    language = st.selectbox("Jazyk textu", ["cs", "en", "auto"], help="Jazyk vstupního textu")

# Hlavní obsah
st.title("Komplexní anonymizační platforma pro české texty")

# Vstupní sekce
st.header("Vstupní text")
input_method = st.radio("Vyberte metodu vstupu:", ("Nahrát soubor", "Vložit text"))

if input_method == "Nahrát soubor":
    uploaded_file = st.file_uploader("Nahrajte soubor (TXT, PDF, DOCX):", type=["txt", "pdf", "docx"])
    if uploaded_file:
        try:
            input_text = read_file_content(uploaded_file)
        except Exception as e:
            st.error(f"Chyba při čtení souboru: {e}")
else:
    input_text = st.text_area("Vložte text k anonymizaci:", height=200)

# Proces anonymizace
if st.button("Anonymizovat"):
    if input_text:
        try:
            # Analýza textu
            with st.spinner('Analyzuji text...'):
                if len(input_text) > 0:
                    results = analyze_text(model_options[selected_model], input_text, selected_categories, threshold=threshold, language=language)
                else:
                    st.warning("Vstupní text je prázdný. Nelze provést analýzu.")
                    results = []
            
            # Vizualizace detekovaných PII
            st.header("Detekované PII")
            highlighted_text = highlight_pii(input_text, results)
            st.markdown(highlighted_text, unsafe_allow_html=True)
            
            # Anonymizace textu
            with st.spinner('Anonymizuji text...'):
                anonymized_text = anonymize_text(
                    text=input_text,
                    operator=anon_method.lower(),
                    analyze_results=results,
                    mask_char='*' if anon_method == "Maskování" else None,
                    chars_to_mask=4 if anon_method == "Maskování" else None
                )

            # Zobrazení výsledků
            st.header("Výsledky anonymizace")
            st.text_area("Anonymizovaný text:", value=anonymized_text, height=200)

            # Výpočet a zobrazení přesnosti
            def calculate_accuracy(original_text, anonymized_text, results):
                total_pii = len(results)
                correctly_anonymized = sum(1 for r in results if anonymized_text[r.start:r.end] != original_text[r.start:r.end])
                return correctly_anonymized / total_pii if total_pii > 0 else 1.0

            accuracy = calculate_accuracy(input_text, anonymized_text, results)
            st.metric("Přesnost anonymizace", f"{accuracy:.2%}")

            # Možnosti exportu
            st.header("Export výsledků")
            export_format = st.selectbox("Formát exportu", ["txt", "json", "csv"])
            export_data = export_results(anonymized_text, results, export_format)
            st.download_button(
                f"Stáhnout anonymizovaný text ({export_format.upper()})",
                export_data,
                f"anonymized_text.{export_format}",
                mime=f"text/{export_format}"
            )

            # Přidání do historie
            if 'history' not in st.session_state:
                st.session_state.history = []
            
            st.session_state.history.append({
                "Model": selected_model,
                "Metoda anonymizace": anon_method,
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
    6. Prohlédněte si detekované PII a výsledky anonymizace.
    7. Vyberte formát exportu a stáhněte anonymizovaný text.
    8. Historie anonymizací je k dispozici ve spodní části stránky.
    """)

# Footer
st.markdown("---")
st.markdown("© 2023 Czech PII Anonymizer. Všechna práva vyhrazena.")