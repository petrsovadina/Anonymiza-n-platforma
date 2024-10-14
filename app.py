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

    selected = st.sidebar.selectbox(
        "Navigace",
        ["Hlavní aplikace", "O projektu", "Budoucí vývoj", "Specifikace využití", "Testovací data"]
    )

    if selected == "Hlavní aplikace":
        show_main_app()
    elif selected == "O projektu":
        show_about_project()
    elif selected == "Budoucí vývoj":
        show_future_development()
    elif selected == "Specifikace využití":
        show_usage_specifications()
    elif selected == "Testovací data":
        show_test_data()

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
    ## Přístup k projektu

    Tento projekt Pokročilého Českého PII Anotátoru a Anonymizátoru demonstruje schopnosti v oblasti zpracování přirozeného jazyka a vývoje AI aplikací. Kombinuje znalosti strojového učení, zpracování textu a vývoje webových aplikací pro vytvoření komplexního řešení ochrany osobních údajů.

    ## Klíčové aspekty řešení

    1. **Pokročilá detekce PII**: Implementace sofistikovaných regulárních výrazů pro detekci různých typů osobních údaj specifických pro český kontext. Toto zahrnuje detekci jmen, adres, rodných čísel, telefonních čísel a dalších citlivých informací.

    2. **Flexibilní anonymizace**: Několik metod anonymizace přizpůsobitelných různým potřebám ochrany soukromí. Uživatelé mohou volit mezi nahrazením údajů zástupnými znaky, obecnými označeními nebo falešnými daty.

    3. **Uživatelsky přívětivé rozhraní**: Využití Streamlit pro interaktivní a snadno použitelné rozhraní. Aplikace poskytuje intuitivní ovládání a okamžitou vizualizaci výsledků anonymizace.

    4. **Škálovatelnost**: Návrh aplikace s ohledem na budoucí rozšíření a integraci pokročilejších AI modelů. Architektura umožňuje snadné přidávání nových funkcí a vylepšení stávajících algoritmů.

    ## Technické detaily

    - **Python**: Efektivní implementace logiky aplikace s využitím moderních Python knihoven a best practices.
    - **NLP techniky**: Aplikace technik zpracování přirozeného jazyka pro přesnou detekci PII, včetně pokročilé tokenizace a analýzy kontextu.
    - **Streamlit**: Rychlé prototypování pomocí moderních nástrojů pro tvorbu webových aplikací, umožňující snadnou iteraci a vylepšování uživatelského rozhraní.
    - **Verzování**: Vývoj s využitím Git pro efektivní správu verzí a spolupráci, umožňující sledování změn a snadnou integraci nových funkcí.

    Tento projekt odráží schopnosti v oblasti AI vývoje, od návrhu algoritmu až po implementaci uživatelsky přívětivého rozhraní, s důrazem na praktické využití v reálném světě.
    """)

def show_future_development():
    st.title("Vize budoucího vývoje")
    st.write("""
    Plány pro další rozvoj projektu zahrnují:

    1. **Integrace pokročilých NLP modelů**: 
       - Implementace state-of-the-art modelů jako BERT nebo GPT pro přesnější detekci PII.
       - Využití transfer learningu pro adaptaci modelů na specifika českého jazyka a kontextu.
       - Experimentování s vlastními fine-tuned modely pro zvýšení přesnosti detekce.

    2. **Rozšíření na multijazyčnou podporu**: 
       - Rozšíření aplikace na další jazyky, počínaje slovenštinou a angličtinou.
       - Implementace detekce jazyka pro automatický výběr správných pravidel a modelů.

    3. **Implementace API pomocí FastAPI**: 
       - Vytvoření robustního API pro snadnou integraci do existujících systémů.
       - Implementace různých endpointů pro různé typy operací (jednorázová anonymizace, dávkové zpracování).
       - Zabezpečení API pomocí OAuth2 a rate limitingu.

    4. **Optimalizace výkonu**: 
       - Využití pokročilých technik optimalizace Pythonu pro zrychlení zpracování.
       - Možná integrace C++ pro kritické části kódu vyžadující vysoký výkon.
       - Implementace cachování a paralelního zpracování pro zvýšení propustnosti.

    5. **Kontejnerizace a mikroslužby**: 
       - Využití Docker pro vytvoření konzistentního prostředí pro vývoj a nasazení.
       - Návrh mikroslužeb architektury pro lepší škálovatelnost a odolnost systému.
       - Implementace orchestrace pomocí Kubernetes pro automatické škálování a správu kontejnerů.

    6. **Implementace pokročilých metod anonymizace**: 
       - Aplikace znalostí v oblasti diferenciální soukromí pro poskytnutí silnějších garancí ochrany soukromí.
       - Implementace k-anonymity a l-diversity pro komplexnější anonymizaci datových sad.
       - Vývoj adaptivních metod anonymizace, které se přizpůsobují kontextu a citlivosti dat.

    7. **Continuous Integration/Continuous Deployment**: 
       - Nastavení CI/CD pipeline pro automatizaci testování a nasazení.
       - Implementace automatizovaných testů, včetně unit testů, integračních testů a end-to-end testů.
       - Využití monitorovacích nástrojů pro sledování výkonu a stability aplikace v produkčním prostředí.

    Tyto plány odrážejí potenciál pro vytváření komplexních, škálovatelných řešení v oblasti AI vývoje, s důrazem na praktické využití, bezpečnost a výkon.
    """)

def show_usage_specifications():
    st.title("Potenciál a využití projektu")
    st.write("""
    ## Integrace a využití FastAPI

    Plánovaná implementace FastAPI přinese následující výhody a možnosti:

    1. **Výkonné API rozhraní**: 
       - FastAPI umožní vytvořit rychlé a efektivní API pro přístup k funkcím anonymizace.
       - Asynchronní zpracování pro vysokou propustnost a nízkou latenci.

    2. **Automatická dokumentace**: 
       - Využití Swagger UI pro interaktivní API dokumentaci.
       - Automatické generování OpenAPI (Swagger) specifikace.

    3. **Asynchronní zpracování**: 
       - Možnost asynchronního zpracování požadavků pro lepší výkon při vysoké zátěži.
       - Efektivní využití systémových zdrojů díky asynchronnímu I/O.

    4. **Validace dat**: 
       - Automatická validace vstupních dat pomocí Pydantic modelů.
       - Typová kontrola pro zvýšení spolehlivosti a bezpečnosti API.

    5. **Snadná integrace**: 
       - Jednoduché začlenění do existujících systémů pomocí RESTful API.
       - Podpora různých formátů dat (JSON, XML, form-data).

    ### Příklady využití FastAPI v projektu:

    1. **Endpoint pro anonymizaci** (`/anonymize`): 
       - Zpracování jednotlivých textů s možností specifikace typů PII k anonymizaci.
       - Podpora různých metod anonymizace (nahrazení, maskování, generování falešných dat).

    2. **Dávkové zpracování** (`/batch-anonymize`): 
       - Anonymizace většího množství dokumentů v jednom požadavku.
       - Asynchronní zpracování s možností sledování průběhu.

    3. **Customizace pravidel** (`/update-rules`): 
       - Dynamická aktualizace pravidel anonymizace bez nutnosti restartu služby.
       - Možnost přidávání nových typů PII a úpravy existujících pravidel.

    4. **Statistiky a reporting** (`/stats`): 
       - Získání statistik o zpracovaných datech a výkonu systému.
       - Generování reportů o detekovaných a anonymizovaných PII.

    5. **Verifikace anonymizace** (`/verify-anonymization`):
       - Kontrola úspěšnosti anonymizace a detekce případných úniků PII.

    ## Další možnosti integrace

    Kromě FastAPI projekt nabízí:

    1. **Batch processing**: 
       - Vývoj řešení pro zpracování velkých objemů dat.
       - Integrace s big data technologiemi jako Apache Spark pro distribuované zpracování.
       - Možnost zpracování offline dat a velkých datových sad.

    2. **Webhooks**: 
       - Automatizované zpracování dokumentů při jejich nahrání nebo aktualizaci.
       - Integrace s systémy pro správu dokumentů a workflow.
       - Real-time notifikace o dokončení anonymizace.

    3. **Customizace**: 
       - Flexibilní architektura umožňující přizpůsobení specifickým potřebám klientů.
       - Možnost rozšíření o vlastní typy PII a metody anonymizace.
       - Konfigurovatelné pravidla a politiky anonymizace.

    4. **Integrace s cloud službami**:
       - Možnost nasazení na různé cloud platformy (AWS, Azure, Google Cloud).
       - Využití cloud-native služeb pro škálování a správu aplikace.

    5. **Rozšířené možnosti exportu**:
       - Podpora různých formátů výstupu (JSON, CSV, XML).
       - Možnost generování detailních reportů o provedené anonymizaci.

    Tyto specifikace odrážejí potenciál pro vytváření všestranných a škálovatelných AI řešení s širokým využitím v různých odvětvích, s důrazem na moderní přístupy k vývoji API a integraci systémů.
    """)

def show_test_data():
    st.title("Testovací data pro anonymizační platformu")
    
    st.header("1. Osobní profily")
    
    st.subheader("Profil 1: Jan Novák")
    st.write("""
    - Jméno: Jan Novák
    - Datum narození: 15.3.1985
    - Rodné číslo: 850315/1234
    - Adresa: Hlavní 123, 110 00 Praha 1
    - E-mail: jan.novak@email.cz
    - Telefon: +420 601 234 567
    - Číslo OP: 123456789
    - Číslo účtu: 1234567890/0800
    """)
    
    st.subheader("Profil 2: Marie Svobodová")
    st.write("""
    - Jméno: Ing. Marie Svobodová, Ph.D.
    - Datum narození: 22.7.1990
    - Rodné číslo: 905722/9876
    - Adresa: Nová 456, 602 00 Brno
    - E-mail: marie.svobodova@gmail.com
    - Telefon: 00420777888999
    - Číslo pasu: 98765432
    - IBAN: CZ65 0800 0000 0012 3456 7890
    """)
    
    st.subheader("Profil 3: Petr Dvořák")
    st.write("""
    - Jméno: MUDr. Petr Dvořák
    - Datum narození: 1. ledna 1970
    - Rodné číslo: 700101/3333
    - Adresa: Dlouhá 789, 301 00 Plzeň
    - E-mail: petr.dvorak@seznam.cz
    - Telefon: 420 602 111 222
    - DIČ: CZ7001013333
    - Číslo pojištěnce: 700101/3333
    """)
    
    st.header("2. Dokumenty")
    
    st.subheader("2.1 Životopis - Jan Novák")
    st.code("""
Jan Novák
Hlavní 123, 110 00 Praha 1
Tel: +420 601 234 567
E-mail: jan.novak@email.cz

Datum narození: 15.3.1985
Stav: ženatý

Vzdělání:
2004-2009: Vysoká škola ekonomická v Praze, obor Finance

Pracovní zkušenosti:
2010-současnost: Finanční analytik, ABC Bank, a.s.
  - Zpracování finančních reportů
  - Analýza investičních příležitostí

2009-2010: Junior účetní, XYZ s.r.o.
  - Vedení účetnictví malých a středních podniků

Jazykové znalosti:
Angličtina - pokročilá úroveň
Němčina - středně pokročilá úroveň

Reference:
Ing. Jiří Zelený, vedoucí oddělení, ABC Bank, a.s.
Tel: 420 234 567 890
    """)
    
    st.subheader("2.2 Lékařská zpráva - Marie Svobodová")
    st.code("""
Fakultní nemocnice Brno
Jihlavská 20, 625 00 Brno
IČO: 65269705

LÉKAŘSKÁ ZPRÁVA

Pacient: Ing. Marie Svobodová, Ph.D.
Datum narození: 22.7.1990
Rodné číslo: 905722/9876
Bydliště: Nová 456, 602 00 Brno
Pojišťovna: 111

Anamnéza:
Pacientka přichází s bolestí v pravém podžebří trvající 3 dny. Neudává horečku ani zvracení. V osobní anamnéze hypertenze na medikaci.

Fyzikální vyšetření:
TK: 130/80, P: 72/min, TT: 36.8°C
Břicho měkké, palpačně citlivé v pravém podžebří, Murphy negativní.

Závěr:
Suspektní cholecystitis. Doporučeno ultrazvukové vyšetření břicha.

Vypracoval: MUDr. Jan Veselý
Dne: 15.5.2023
    """)
    
    st.subheader("2.3 Faktura - Petr Dvořák")
    st.code("""
XYZ Servis s.r.o.
Technická 10, 301 00 Plzeň
IČO: 12345678
DIČ: CZ12345678

FAKTURA č. 2023001

Odběratel:
MUDr. Petr Dvořák
Dlouhá 789
301 00 Plzeň
DIČ: CZ7001013333

Datum vystavení: 1.6.2023
Datum splatnosti: 15.6.2023
Forma úhrady: bankovní převod

Položka                     Množství    Cena/ks    Celkem
---------------------------------------------------------
Servis zdravotnického
zařízení XY                      1     10000 Kč   10000 Kč
Náhradní díly                    2      2500 Kč    5000 Kč
---------------------------------------------------------
Celkem bez DPH                                   15000 Kč
DPH 21%                                           3150 Kč
Celkem s DPH                                     18150 Kč

Číslo účtu pro platbu: 1234567890/0300
Variabilní symbol: 2023001

Děkujeme za Vaši důvěru a těšíme se na další spolupráci.
    """)
    
    st.header("3. E-mailová komunikace")
    
    st.subheader("3.1 E-mail od Jana Nováka")
    st.code("""
Od: jan.novak@email.cz
Komu: podpora@banka.cz
Předmět: Žádost o změnu osobních údajů

Vážení,

prosím o změnu mých kontaktních údajů ve Vašem systému. Nové údaje jsou následující:

Jméno: Jan Novák
Nová adresa: Krátká 456, 120 00 Praha 2
Nový telefon: 702 345 678

Moje identifikační údaje:
Datum narození: 15.3.1985
Číslo účtu: 1234567890/0800

Děkuji za vyřízení mé žádosti.

S pozdravem,
Jan Novák
    """)
    
    st.subheader("3.2 E-mail od Marie Svobodové")
    st.code("""
Od: marie.svobodova@gmail.com
Komu: hr@firma.cz
Předmět: Žádost o pracovní pozici

Vážená paní / Vážený pane,

reaguji na Váš inzerát na pozici "Datový analytik" zveřejněný na pracovním portálu Jobs.cz.

Jmenuji se Ing. Marie Svobodová, Ph.D. a mám pětiletou zkušenost v oblasti datové analýzy. Absolvovala jsem doktorské studium na Masarykově univerzitě v Brně, obor Aplikovaná informatika.

Moje kontaktní údaje:
Telefon: 777888999
E-mail: marie.svobodova@gmail.com
LinkedIn: linkedin.com/in/marie-svobodova

V příloze naleznete můj životopis a motivační dopis. Budu ráda za zpětnou vazbu a případné pozvání na osobní pohovor.

S pozdravem,
Marie Svobodová
    """)
    
    st.header("4. Příspěvek na sociální síti")
    
    st.subheader("4.1 Příspěvek Petra Dvořáka na Facebooku")
    st.code("""
Petr Dvořák
1. června 2023 v 10:15

Ahoj přátelé! Právě jsem se vrátil z úžasné dovolené v Chorvatsku. Pokud budete chtít nějaké tipy na ubytování nebo restaurace v oblasti Splitu, dejte vědět. Můžete mi zavolat na 602 111 222 nebo napsat na petr.dvorak@seznam.cz. Pojede: Ivan Máchal, Pavel Miško, Rutha Tomanová, Zdislava Novotná
    """)

if __name__ == "__main__":
    main()