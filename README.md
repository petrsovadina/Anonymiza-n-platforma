
# Anonymizační platforma pro české texty

## 📖 Úvod

Tento projekt je zaměřen na návrh a implementaci systému pro automatické odstranění osobních údajů (PII) z interních dokumentů. Systém je navržen pro ochranu soukromí a bezpečnost při použití těchto dokumentů jako zdrojů pro jazykové modely (LLM).

## 🚀 Klíčové funkce

- **Detekce PII**: Automatické rozpoznávání osobních identifikačních údajů v českých textech.
- **Různé metody anonymizace**: Uživatelé mohou vybrat různé způsoby odstranění nebo maskování PII (hvězdičky, obecné pojmy, apod.).
- **Podpora formátů**: Zpracování textů ve formátech .txt, .pdf, .docx.
- **Uživatelské rozhraní**: Intuitivní a snadno použitelné UI postavené na Streamlit.
- **Historie anonymizací**: Možnost uchování historie anonymizací pro budoucí použití nebo audit.
- **Export dat**: Umožňuje stažení anonymizovaných dokumentů v podporovaných formátech.

## 🛠️ Použité technologie

- **Python**: Hlavní programovací jazyk projektu.
- **FastAPI**: Zajišťuje RESTful API pro backend.
- **Streamlit**: Slouží k vytvoření uživatelského rozhraní.
- **Microsoft Presidio**: Knihovna pro detekci a anonymizaci osobních údajů (PII).
- **Piiranha**: Knihovna pro detekci osobních údajů specificky přizpůsobená pro češtinu.
- **Transformers**: Modely strojového učení pro pokročilé zpracování textu.
- **OpenAI API**: Volitelně pro pokročilé funkce jako generování syntetických dat a kontextová anonymizace.

## 📦 Instalace

1. **Naklonujte repozitář**:
   ```bash
   git clone https://github.com/username/anonymizacni-platforma.git
   cd anonymizacni-platforma
   ```

2. **Vytvořte a aktivujte virtuální prostředí**:
   - Na Unixových systémech (Linux, macOS):
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
   - Na Windows:
     ```bash
     python -m venv venv
     venv\Scriptsctivate
     ```

3. **Nainstalujte požadované závislosti**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Spusťte aplikaci**:
   ```bash
   streamlit run app.py
   ```

## 🖥️ Použití

1. Otevřete webový prohlížeč a přejděte na [http://localhost:8501](http://localhost:8501).
2. Nahrajte dokument nebo vložte text, který chcete anonymizovat.
3. Vyberte metodu anonymizace a nechte systém provést anonymizaci.
4. Zkontrolujte výsledky anonymizace a případně si stáhněte anonymizovaný dokument.

## 📅 Harmonogram vývoje

- **Průzkum a návrh**: Definování metod a výběr nástrojů pro anonymizaci.
- **Implementace**: Vývoj detekčních a anonymizačních funkcí.
- **Testování**: Ověření správnosti anonymizace a detekce PII.
- **Nasazení**: Implementace a zajištění funkčnosti pro reálné použití.

## 📜 Licence

Projekt je licencován pod licencí MIT. Více informací naleznete v [LICENSE](./LICENSE).
