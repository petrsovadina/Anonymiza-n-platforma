import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Python version:", sys.version)
print("Python path:", sys.path)
import site
print("Site packages:", site.getsitepackages())

import streamlit as st
# Odstraňte nebo zakomentujte tento řádek
# from streamlit_option_menu import option_menu
import re
from faker import Faker
import json
import pandas as pd

# Odstraňte nebo zakomentujte tyto řádky
# from src.czech_anonymization.analyzers import custom_recognizers
# from src.czech_anonymization.processors import document_processors

# Initialize Faker for Czech
fake = Faker('cs_CZ')

# Enhanced PII patterns (simplified for brevity)
PII_PATTERNS = {
    'JMÉNO': r'\b(?:(?:Ing\.|Mgr\.|JUDr\.|MUDr\.|PhDr\.|RNDr\.|doc\.|prof\.|Dr\.) )?[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+(?:[ -][A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+)*(?:(,? (?:CSc\.|DrSc\.|Ph\.D\.))?)\b',
    'RODNÉ_ČÍSLO': r'\b\d{6}/\d{3,4}\b',
    'DATUM_NAROZENÍ': r'\b(?:\d{1,2}\.? )?(?:\d{1,2}\.? )?(?:\d{4}|(?:led(?:na|en)|únor(?:a)?|břez(?:na|en)|dub(?:na|en)|květ(?:na|en)|červ(?:na|en)(?:ec)?|srp(?:na|en)|září|říj(?:na|en)|listopa(?:du|d)|prosine(?:c|e)) ?\d{4})\b',
    'TELEFON': r'\b(?:\+420 ?)?(?:(?:\d{3} ?){3}|\d{9})\b',
    'EMAIL': r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
    'ADRESA': r'\b[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+(?:[ -][A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+)* \d+(?:/\d+[a-zA-Z]?)?,?\s*\d{3} ?\d{2} [A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+(?:[ -][A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+)*\b',
    'ČÍSLO_OP': r'\b(?:\d{9}|\d{6} ?\d{3})\b',
    'ČÍSLO_PASU': r'\b[A-Z]{2}\d{7}\b',
    'BANKOVNÍ_ÚČET': r'\b\d{1,6}-?\d{2,10}/\d{4}\b',
    'IČO': r'\b\d{8}\b',
    'DIČ': r'\bCZ\d{8,10}\b',
    'DATOVÁ_SCHRÁNKA': r'\b[a-zA-Z0-9]{7}\b'
}

def detect_and_anonymize_pii(text, selected_pii_types, anonymization_method):
    entities = []
    anonymized_text = text

    for entity_type, pattern in PII_PATTERNS.items():
        if entity_type in selected_pii_types:
            for match in re.finditer(pattern, text):
                entities.append({
                    'start': match.start(),
                    'end': match.end(),
                    'text': match.group(),
                    'type': entity_type
                })

    # Sort entities in reverse order to avoid index issues when replacing
    entities.sort(key=lambda x: x['start'], reverse=True)

    for entity in entities:
        anonymized_value = anonymize_entity(entity, anonymization_method)
        anonymized_text = anonymized_text[:entity['start']] + anonymized_value + anonymized_text[entity['end']:]

    return {'original_text': text, 'anonymized_text': anonymized_text, 'entities': entities}

def anonymize_entity(entity, method):
    if method == 'Nahradit X':
        return 'X' * len(entity['text'])
    elif method == 'Nahradit [TYP_ÚDAJE]':
        return f"[{entity['type']}]"
    elif method == 'Použít falešná data':
        if entity['type'] == 'JMÉNO':
            return fake.name()
        elif entity['type'] == 'RODNÉ_ČÍSLO':
            return fake.ssn()
        elif entity['type'] == 'DATUM_NAROZENÍ':
            return fake.date(pattern='%d.%m.%Y')
        elif entity['type'] == 'TELEFON':
            return fake.phone_number()
        elif entity['type'] == 'EMAIL':
            return fake.email()
        elif entity['type'] == 'ADRESA':
            return fake.address()
        else:
            return fake.word()
    return entity['text']

def main():
    st.set_page_config(page_title="Český PII Anotátor a Anonymizátor", layout="wide")

    # Nahraďte option_menu standardním Streamlit selectboxem
    selected = st.sidebar.selectbox(
        "Navigace",
        ["Hlavní aplikace", "O projektu", "Budoucí vývoj", "Specifikace využití"]
    )

    if selected == "Hlavní aplikace":
        show_main_app()
    elif selected == "O projektu":
        show_about_project()
    elif selected == "Budoucí vývoj":
        show_future_development()
    elif selected == "Specifikace využití":
        show_usage_specifications()

def show_main_app():
    st.title("Pokročilý Český PII Anotátor a Anonymizátor")

    text_input = st.text_area("Zadejte český text k analýze:", height=200)

    selected_pii_types = st.multiselect(
        "Vyberte typy PII k detekci:",
        list(PII_PATTERNS.keys()),
        default=list(PII_PATTERNS.keys())
    )

    anonymization_method = st.selectbox(
        "Vyberte metodu anonymizace:",
        ["Nahradit X", "Nahradit [TYP_ÚDAJE]", "Použít falešná data"]
    )

    if st.button("Analyzovat a Anonymizovat"):
        if not text_input:
            st.error("Prosím, zadejte nějaký text k analýze.")
        elif not selected_pii_types:
            st.error("Prosím, vyberte alespoň jeden typ PII k detekci.")
        else:
            result = detect_and_anonymize_pii(text_input, selected_pii_types, anonymization_method)
            
            st.subheader("Výsledky anonymizace")
            st.write(f"Anonymizace proběhla úspěšně, bylo detekováno a anonymizováno {len(result['entities'])} osobních údajů.")

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Původní text")
                st.text_area("", result['original_text'], height=300)
            with col2:
                st.subheader("Anonymizovaný text")
                st.text_area("", result['anonymized_text'], height=300)

            st.subheader("Detekované PII:")
            pii_summary = {}
            for entity in result['entities']:
                if entity['type'] not in pii_summary:
                    pii_summary[entity['type']] = 1
                else:
                    pii_summary[entity['type']] += 1

            summary_data = [{"Typ PII": k, "Počet instancí": v, "Úspěšnost": "✅"} for k, v in pii_summary.items()]
            st.table(pd.DataFrame(summary_data))

            if st.button("Stáhnout zprávu"):
                report = {
                    "original_text": result['original_text'],
                    "anonymized_text": result['anonymized_text'],
                    "pii_summary": pii_summary
                }
                st.download_button(
                    label="Stáhnout JSON zprávu",
                    data=json.dumps(report, ensure_ascii=False, indent=2),
                    file_name="anonymization_report.json",
                    mime="application/json"
                )

            st.subheader("Zpětná vazba")
            feedback = st.radio("Jste spokojeni s výsledkem anonymizace?", ("Ano", "Ne"))
            comments = st.text_area("Další komentáře:")
            if st.button("Odeslat zpětnou vazbu"):
                st.success("Děkujeme za vaši zpětnou vazbu!")

def show_about_project():
    st.title("O projektu")
    st.write("""
    ## Popis projektu

    Tento projekt je webová aplikace vyvinutá v Pythonu, která slouží k detekci a anonymizaci osobních údajů (PII - Personally Identifiable Information) v českém textu. Aplikace umožňuje uživatelům vložit text, vybrat typy PII k detekci a zvolit metodu anonymizace.

    ## Současný stav projektu

    Projekt je momentálně implementován jako Streamlit aplikace s následujícími hlavními funkcemi:

    1. Vstup textu od uživatele
    2. Výběr typů PII k detekci
    3. Výběr metody anonymizace
    4. Detekce a anonymizace PII v textu
    5. Zobrazení výsledků anonymizace
    6. Možnost stažení zprávy o anonymizaci
    7. Sběr zpětné vazby od uživatelů

    ## Použité technologie

    1. Python 3.9+
    2. Streamlit (verze 1.22.0)
    3. Faker (verze 18.9.0)
    4. Pandas (verze 2.0.2)
    5. Re (standardní knihovna Pythonu)
    6. JSON (standardní knihovna Pythonu)
    """)

def show_future_development():
    st.title("Budoucí vývoj")
    st.write("""
    ## Plány pro budoucí vývoj

    1. Integrace FastAPI
    2. Rozšíření typů PII
    3. Vylepšení metod anonymizace
    4. Optimalizace výkonu
    5. Integrace strojového učení
    6. Rozšíření jazykové podpory
    7. Vylepšení uživatelského rozhraní
    8. Implementace unit testů
    9. Dokumentace API
    10. Kontejnerizace

    ## Účel dalšího vývoje

    Hlavním účelem dalšího vývoje je vytvořit robustní, škálovatelné a snadno integrovatelné řešení pro detekci a anonymizaci PII v českém textu. Toto řešení bude moci být využito v různých odvětvích, jako je zdravotnictví, finance, veřejná správa a další, kde je ochrana osobních údajů klíčová.
    """)

def show_usage_specifications():
    st.title("Specifikace využití")
    st.write("""
    ## Možnosti využití

    1. Zdravotnictví: Anonymizace zdravotních záznamů pro výzkumné účely
    2. Finance: Ochrana osobních údajů klientů v finančních dokumentech
    3. Veřejná správa: Anonymizace úředních dokumentů před jejich zveřejněním
    4. Lidské zdroje: Ochrana osobních údajů zaměstnanců v interních dokumentech
    5. Výzkum a vývoj: Anonymizace dat pro akademický výzkum
    6. E-commerce: Ochrana údajů zákazníků v obchodních transakcích
    7. Sociální média: Anonymizace uživatelských dat pro analýzu trendů

    ## Integrace do existujících systémů

    Plánovaná implementace FastAPI umožní snadnou integraci našeho řešení do existujících systémů a workflow. Toto zahrnuje:

    1. REST API pro detekci a anonymizaci PII
    2. Možnost dávkového zpracování velkých objemů dat
    3. Webhooky pro automatizované zpracování dokumentů
    4. Integrace s populárními platformami pro správu dokumentů

    ## Přizpůsobení pro specifické potřeby

    Naše řešení bude možné přizpůsobit specifickým potřebám různých odvětví a organizací, včetně:

    1. Vlastních typů PII
    2. Specifických metod anonymizace
    3. Integrace s vlastními systémy pro správu dat
    4. Přizpůsobení uživatelského rozhraní
    """)

if __name__ == "__main__":
    main()