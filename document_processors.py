import io
from typing import Union
from PyPDF2 import PdfReader
from docx import Document

def read_txt(file: Union[str, io.BytesIO]) -> str:
    """Čte obsah textového souboru."""
    if isinstance(file, str):
        with open(file, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return file.getvalue().decode('utf-8')

def read_pdf(file: Union[str, io.BytesIO]) -> str:
    """Čte obsah PDF souboru."""
    pdf_reader = PdfReader(file)
    return "\n".join(page.extract_text() for page in pdf_reader.pages)

def read_docx(file: Union[str, io.BytesIO]) -> str:
    """Čte obsah DOCX souboru."""
    doc = Document(file)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)

def read_file_content(file: Union[str, io.BytesIO], file_type: str) -> str:
    """Čte obsah souboru podle jeho typu."""
    if file_type == "text/plain":
        return read_txt(file)
    elif file_type == "application/pdf":
        return read_pdf(file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return read_docx(file)
    else:
        raise ValueError(f"Nepodporovaný typ souboru: {file_type}")