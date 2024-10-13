# Česká Anonymizační Platforma

Tato platforma je navržena pro automatickou detekci a anonymizaci osobních údajů (PII) v českých textech. Využívá pokročilé techniky zpracování přirozeného jazyka a strojového učení pro přesnou a kontextově citlivou anonymizaci.

## Funkce

- Detekce a anonymizace různých typů osobních údajů včetně jmen, e-mailů, telefonních čísel, rodných čísel a dalších.
- Podpora specifických českých formátů osobních údajů.
- Flexibilní nastavení anonymizačních metod.
- Uživatelské rozhraní postavené na Streamlit pro snadné použití a testování.

## Instalace

1. Naklonujte tento repozitář:
   ```
   git clone https://github.com/vas-uzivatelske-jmeno/ceska-anonymizacni-platforma.git
   cd ceska-anonymizacni-platforma
   ```

2. Vytvořte a aktivujte virtuální prostředí:
   ```
   python3.9 -m venv venv
   source venv/bin/activate  # Na Windows použijte `venv\Scripts\activate`
   ```

3. Nainstalujte potřebné závislosti:
   ```
   pip install -r requirements.txt
   ```

4. Stáhněte potřebný jazykový model:
   ```
   python -m spacy download xx_ent_wiki_sm
   ```

## Použití

Pro spuštění Streamlit aplikace použijte:
