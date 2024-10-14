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
    ## Cíl projektu
    
    Jako AI Developer jsem navrhl a implementoval systém pro automatickou detekci a anonymizaci osobních údajů (PII) v českém textu. Tento nástroj jsem vytvořil s cílem pomoci organizacím chránit soukromí jednotlivců při zpracování textových dat, což je klíčové při přípravě dat pro trénování jazykových modelů nebo chatbotů.

    ## Časová osa vývoje

    ### Dosavadní vývoj (3 dny):

    1. **Den 1: Analýza a návrh**
       - Průzkum existujících řešení
       - Definice požadavků a rozsahu projektu
       - Návrh architektury systému

    2. **Den 2: Implementace základní funkcionality**
       - Vývoj modulů pro detekci PII pomocí regulárních výrazů
       - Implementace metod anonymizace
       - Začátek vývoje uživatelského rozhraní

    3. **Den 3: Dokončení prototypu a testování**
       - Dokončení uživatelského rozhraní
       - Implementace generování reportů
       - Základní testování a ladění

    ### Plán budoucího vývoje:

    4. **Dny 4-5: Rozšíření funkcionality**
       - Implementace pokročilých metod anonymizace
       - Rozšíření podpory pro další typy dokumentů
       - Vylepšení uživatelského rozhraní

    5. **Dny 6-8: Implementace NLP modelů**
       - Výběr vhodných NLP modelů pro detekci českých PII
       - Příprava trénovacích dat
       - Implementace a integrace NLP modelů do systému

    6. **Dny 9-11: Trénink a ladění NLP modelů**
       - Trénování NLP modelů na českých datech
       - Fine-tuning modelů pro přesnou detekci PII
       - Testování a vyhodnocení přesnosti modelů

    7. **Dny 12-13: Optimalizace a škálování**
       - Optimalizace výkonu systému
       - Implementace škálovatelného řešení pro zpracování velkých objemů dat
       - Integrace s externími systémy

    8. **Dny 14-15: Finální testování a dokumentace**
       - Komplexní testování celého systému
       - Příprava uživatelské a technické dokumentace
       - Vytvoření demonstračních materiálů

    9. **Den 16: Nasazení a školení**
       - Nasazení systému do produkčního prostředí
       - Školení uživatelů a administrátorů
       - Zahájení podpory a údržby

    Celková odhadovaná pracnost: 16 pracovních dnů

    ## Klíčové aspekty mého řešení

    1. **Pokročilá detekce PII**: Implementoval jsem sofistikované regulární výrazy pro detekci různých typů osobních údajů specifických pro český kontext.

    2. **Flexibilní anonymizace**: Navrhl jsem tři metody anonymizace přizpůsobitelné různým potřebám ochrany soukromí.

    3. **Interaktivní rozhraní**: Využil jsem Streamlit pro vytvoření uživatelsky přívětivého webového rozhraní.

    4. **Customizace**: Implementoval jsem možnost výběru konkrétních typů PII k detekci a anonymizaci.

    5. **Reporting**: Vytvořil jsem systém pro generování přehledných statistik o detekovaných a anonymizovaných údajích.

    ## Algoritmus flow

    Pro lepší pochopení procesu detekce a anonymizace PII jsem vytvořil následující diagram, který ilustruje tok dat a klíčové kroky algoritmu:
    """)
    
    st.image("https://utfs.io/f/z2Za8Zqs0Nofbl54P61Phgi3WHO4xLUXal01qvcmesjT8KJp", caption="Diagram algoritmu flow pro detekci a anonymizaci PII")

    st.write("""
    Tento diagram ukazuje hlavní komponenty systému a jejich vzájemné interakce, od vstupu textu přes detekci PII až po výstup anonymizovaného textu a generování reportu.

    ## Technologie a nástroje

    Při vývoji tohoto projektu jsem využil následující technologie a knihovny:

    - **Python**: Hlavní programovací jazyk pro implementaci logiky.
    - **Streamlit**: Pro vytvoření interaktivního webového rozhraní.
    - **Regex**: Využití pokročilých regulárních výrazů pro přesnou detekci PII.
    - **Faker**: Generování realistických falešných dat pro anonymizaci.
    - **Pandas**: Zpracování a vizualizace statistik o detekovaných PII.

    V budoucích fázích projektu plánuji integraci pokročilých NLP modelů pro ještě přesnější detekci českých PII.

    ## Využití pro přípravu dat

    Tento systém hraje klíčovou roli v procesu přípravy dat pro různé účely, včetně:

    1. **Ochrana soukromí**: Anonymizace osobních údajů v dokumentech před jejich dalším zpracováním nebo sdílením.
    2. **Příprava trénovacích dat**: Bezpečná příprava textových dat pro trénování jazykových modelů nebo chatbotů.
    3. **Compliance**: Pomoc při dodržování předpisů o ochraně osobních údajů, jako je GDPR.
    4. **Analýza dat**: Umožnění bezpečné analýzy textových dat bez rizika úniku citlivých informací.

    Tento projekt demonstruje mou schopnost navrhnout a implementovat komplexní řešení pro ochranu osobních údajů s důrazem na praktické využití v reálném světě, zejména v kontextu zpracování a analýzy textových dat v českém jazyce.
    """)

def show_future_development():
    st.title("Plán vývoje a nasazení")
    st.write("""
    ## Integrace s chatbotem pomocí FastAPI a LangChain

    Pro efektivní využití našeho anonymizačního nástroje v systému chatbota implementujeme následující:

    1. **FastAPI Endpoints**:
       - `/anonymize`: POST endpoint pro anonymizaci jednotlivých textů
       - `/batch-anonymize`: POST endpoint pro dávkové zpracování většího množství dokumentů
       - `/update-rules`: PUT endpoint pro aktualizaci pravidel anonymizace
       - `/get-stats`: GET endpoint pro získání statistik o zpracovaných datech

    2. **API Dokumentace**:
       - Využití Swagger UI pro interaktivní API dokumentaci
       - Detailní popis všech endpointů, včetně vstupních a výstupních schémat
       - Příklady použití pro každý endpoint

    3. **Integrace s LangChain**:
       - Vytvoření custom LangChain tool pro anonymizaci dat
       - Implementace LangChain agent, který bude využívat náš anonymizační nástroj
       - Nastavení workflow pro automatické zpracování dokumentů před jejich použitím v chatbotu

    4. **Příklad využití v LangChain**:
    ```python
    from langchain.agents import Tool
    from langchain.agents import initialize_agent
    from langchain.llms import OpenAI

    # Definice našeho anonymizačního nástroje
    anonymization_tool = Tool(
        name="Anonymization",
        func=lambda x: requests.post("http://our-api.com/anonymize", json={"text": x}).json()["anonymized_text"],
        description="Useful for anonymizing text containing personal information"
    )

    # Inicializace agenta
    llm = OpenAI(temperature=0)
    agent = initialize_agent([anonymization_tool], llm, agent="zero-shot-react-description", verbose=True)

    # Použití agenta
    agent.run("Anonymize this text and then summarize it: 'Jan Novák, born on 15.3.1985, lives at Hlavní 123, Prague.'")
    ```

    ## AI a NLP modely pro detekci PII

    V budoucím vývoji plánujeme integraci pokročilých NLP a NER (Named Entity Recognition) modelů pro zlepšení detekce osobních údajů:

    ### Výhody NER modelů pro náš projekt:

    NER modely jsou ideální pro klasifikaci a anonymizaci textu díky své schopnosti přesně identifikovat pojmenované entity a strukturovaně kategorizovat citlivé údaje. Oproti jiným AI modelům poskytují přesnější výsledky při detekci citlivých informací, což je zásadní pro zajištění ochrany osobních údajů a správnou kategorizaci textů podle jejich obsahu.

    ### Plánované využití NLP a NER modelů:

    1. **Přesnější detekce PII**: Využití pre-trénovaných modelů pro identifikaci širšího spektra osobních údajů.
    2. **Kontextová analýza**: Schopnost rozpoznat PII i v méně zřejmých kontextech.
    3. **Multijazyčná podpora**: Rozšíření detekce PII na více jazyků.
    4. **Adaptivní učení**: Možnost doučování modelů na specifických datech klienta.

    ### Vhodné modely pro detekci PII:

    - FacebookAI/xlm-roberta-large-finetuned-conll03-english: Pro multijazyčnou detekci entit.
    - iiiorg/piiranha-v1-detect-personal-information: Specializovaný model pro detekci osobních informací.
    - Microsoft Presidio: Framework pro detekci a anonymizaci, který můžeme integrovat do našeho řešení.

    ### Implementace:

    1. Využití Transformers knihovny pro integraci a fine-tuning modelů.
    2. Vytvoření pipeline pro kombinaci rule-based přístupu s NER modely.
    3. Implementace mechanismu pro pravidelné aktualizace a doučování modelů.

    Integrace těchto pokročilých NLP a NER modelů významně zvýší přesnost a robustnost našeho anonymizačního nástroje, což umožní jeho využití i v náročnějších scénářích a pro komplexnější typy dokumentů.
    """)

def show_usage_specifications():
    st.title("Specifikace využití")
    st.write("""
    ## Způsoby anonymizace

    Systém nabízí tři hlavní metody anonymizace osobních údajů:

    1. **Nahrazení zástupnými znaky**: Osobní údaje jsou nahrazeny řetězcem 'X' stejné délky.
    2. **Nahrazení obecnými pojmy**: Osobní údaje jsou nahrazeny obecným označením typu údaje (např. [JMÉNO], [ADRESA]).
    3. **Použití falešných dat**: Osobní údaje jsou nahrazeny realisticky vypadajícími, ale fiktivními daty.

    ## Testování a ověření

    Pro zajištění správnosti a úplnosti anonymizace systém zahrnuje:

    1. **Generování testovacích dat**: Možnost vytvářet fiktivní dokumenty s osobními údaji pro testování.
    2. **Statistiky detekce**: Přehled detekovaných a anonymizovaných údajů pro každý dokument.
    3. **Vizuální porovnání**: Možnost porovnat původní a anonymizovaný text pro kontrolu.

    ## Vstupní data

    Systém je navržen pro zpracování:

    1. Libovolného textu zadaného uživatelem.
    2. Generovaných falešných dat pro testovací účely.
    3. (V budoucnu) Různých formátů dokumentů (TXT, PDF, DOC).

    ## Zdůvodnění výběru nástrojů

    1. **Python**: Široká podpora pro NLP a zpracování textu, rozsáhlý ekosystém knihoven.
    2. **Streamlit**: Rychlé vytvoření interaktivního rozhraní pro demonstraci funkčnosti.
    3. **Regex**: Efektivní a flexibilní nástroj pro detekci vzorů v textu.
    4. **Faker**: Generování realistických falešných dat pro testování a anonymizaci.

    Tato kombinace nástrojů umožňuje rychlý vývoj, snadnou údržbu a potenciál pro budoucí rozšíření systému.
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