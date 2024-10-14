# Pokročilý Český PII Anotátor a Anonymizátor

Tento projekt představuje systém pro automatickou detekci a anonymizaci osobních údajů (PII - Personally Identifiable Information) v českém textu. Je navržen jako nástroj pro přípravu dat pro jazykové modely a chatboty, s důrazem na ochranu osobních údajů.

## Funkce

- Detekce různých typů PII v českém textu (jména, adresy, rodná čísla, telefonní čísla, e-maily, atd.)
- Tři metody anonymizace: nahrazení znakem 'X', obecnými pojmy, nebo falešnými daty
- Interaktivní webové rozhraní pro snadné použití a testování
- Generování statistik a reportů o anonymizovaných datech
- Možnost customizace typů PII k detekci

## Instalace

1. Naklonujte tento repozitář
2. Ujistěte se, že máte nainstalovaný Python 3.9 nebo novější
3. Vytvořte virtuální prostředí: `python -m venv venv`
4. Aktivujte virtuální prostředí:
   - Na Windows: `venv\Scripts\activate`
   - Na macOS a Linux: `source venv/bin/activate`
5. Nainstalujte závislosti: `pip install -r requirements.txt`

## Spuštění aplikace

Po instalaci spusťte aplikaci příkazem:

```
streamlit run app.py
```

## Struktura projektu

- `app.py`: Hlavní soubor aplikace obsahující logiku Streamlit rozhraní a funkce pro anonymizaci
- `src/czech_anonymization/`: Adresář pro moduly specifické pro českou anonymizaci
- `requirements.txt`: Seznam závislostí projektu

## Použité technologie

- Python 3.9+
- Streamlit: Pro vytvoření interaktivního webového rozhraní
- Faker: Pro generování falešných dat
- Pandas: Pro zpracování a zobrazení dat
- Regex: Pro detekci vzorů PII v textu

## Funkce aplikace

1. **Hlavní aplikace**: Umožňuje uživatelům zadat text, vybrat typy PII k detekci a metodu anonymizace.
2. **O projektu**: Poskytuje informace o projektu a jeho cílech.
3. **Budoucí vývoj**: Nastiňuje plány pro budoucí vylepšení a rozšíření funkcionality.
4. **Specifikace využití**: Detailní popis způsobů anonymizace, testování a vstupních dat.
5. **Testovací data**: Nabízí vzorové profily a dokumenty pro testování anonymizace.
