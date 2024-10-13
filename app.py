import streamlit as st
from src.main import create_analyzer
from src.czech_anonymization.processors.document_processors import anonymize_czech_text

# Inicializace analyzátoru
analyzer = create_analyzer()

st.set_page_config(page_title="Česká Anonymizační Platforma", page_icon="🕵️", layout="wide")

st.title("Česká Anonymizační Platforma")

st.markdown("""
Tato aplikace umožňuje anonymizaci osobních údajů v českém textu. 
Vložte text obsahující osobní údaje a nechte naši platformu provést anonymizaci.
""")

# Vstupní textové pole
input_text = st.text_area("Vložte text k anonymizaci:", height=200)

# Tlačítko pro anonymizaci
if st.button("Anonymizovat"):
    if input_text:
        # Provedení anonymizace
        anonymized_text = anonymize_czech_text(input_text, analyzer)
        
        # Zobrazení výsledku
        st.subheader("Anonymizovaný text:")
        st.text_area("", anonymized_text, height=200)
        
        # Statistiky
        original_words = len(input_text.split())
        anonymized_words = len(anonymized_text.split())
        st.info(f"Počet slov v původním textu: {original_words}")
        st.info(f"Počet slov v anonymizovaném textu: {anonymized_words}")
    else:
        st.warning("Prosím, vložte text k anonymizaci.")

# Přidání informací o projektu
st.sidebar.title("O projektu")
st.sidebar.info(
    "Tato aplikace je ukázkou České Anonymizační Platformy, "
    "která automaticky detekuje a anonymizuje osobní údaje v českém textu. "
    "Využívá pokročilé techniky zpracování přirozeného jazyka a strojového učení."
)

# Přidání příkladů použití
st.sidebar.title("Příklady použití")
example_text = """
Jan Novák, narozený 15.3.1980, bydlí na adrese Dlouhá 123, Praha 1, 110 00. 
Jeho e-mailová adresa je jan.novak@example.com a telefonní číslo 123 456 789. 
Číslo jeho občanského průkazu je AB123456 a rodné číslo 800315/1234.
"""
if st.sidebar.button("Vložit ukázkový text"):
    st.text_area("Vložte text k anonymizaci:", example_text, height=200)

# Footer
st.markdown("---")
st.markdown("© 2023 Česká Anonymizační Platforma | Vytvořeno s ❤️ pomocí Streamlit")
