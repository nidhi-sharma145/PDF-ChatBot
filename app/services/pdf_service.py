import io
from typing import List
import pypdf

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts all text content from raw PDF bytes.
    
    Args:
        file_bytes: The raw binary bytes of the PDF file.
        
    Returns:
        A combined string of all extracted text.
    """
    extracted_text = []
    pdf_file = io.BytesIO(file_bytes)
    
    try:
        reader = pypdf.PdfReader(pdf_file)
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                extracted_text.append(page_text)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF document: {str(e)}")
        
    return "\n\n".join(extracted_text)

def split_text_into_chunks(text: str, chunk_size: int = 600, chunk_overlap: int = 100) -> List[str]:
    """
    Splits a large block of text into smaller overlapping chunks.
    
    This preserves semantic context across chunks and optimizes retrieval accuracy.
    
    Args:
        text: The raw source text.
        chunk_size: Maximum character count per chunk.
        chunk_overlap: Number of characters to overlap between adjacent chunks.
        
    Returns:
        A list of split text chunks.
    """
    if not text or not text.strip():
        return []
        
    # Clean up excessive or double white spaces
    cleaned_text = " ".join(text.split())
    
    chunks = []
    start = 0
    text_length = len(cleaned_text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        
        # If not at the end of the text, try to find a natural boundary (space or newline)
        if end < text_length:
            # Look backwards up to 30 characters for a whitespace boundary
            boundary = cleaned_text.rfind(' ', end - 30, end)
            if boundary != -1:
                end = boundary
                
        chunk = cleaned_text[start:end].strip()
        if chunk:
            chunks.append(chunk)
            
        # Ensure we strictly advance and never go backwards or get stuck in negative indices
        next_start = end - chunk_overlap
        if next_start <= start or next_start < 0:
            start = end
        else:
            start = next_start
            
    return chunks
