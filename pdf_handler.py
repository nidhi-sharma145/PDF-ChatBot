import fitz  # PyMuPDF
import re

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from a given PDF file."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def clean_text(text: str) -> str:
    """Removes extra whitespaces and newlines."""
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def split_text_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Splits text into chunks of specified size with some overlap."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def process_pdf(file_path: str) -> list[str]:
    """Extracts, cleans, and chunks text from a PDF."""
    raw_text = extract_text_from_pdf(file_path)
    cleaned_text = clean_text(raw_text)
    chunks = split_text_into_chunks(cleaned_text)
    return chunks
