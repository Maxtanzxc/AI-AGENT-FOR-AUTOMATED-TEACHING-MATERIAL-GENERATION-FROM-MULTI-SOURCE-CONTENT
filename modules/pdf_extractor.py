import fitz  # PyMuPDF
import os
from modules.ocr_extractor import ocr_pdf_page, is_ocr_available

def extract_text_from_pdf(pdf_path: str, use_ocr_fallback: bool = True) -> str:
    """
    Extract clean text from a PDF file.
    If digital text is sparse/missing and OCR is available, automatically falls back
    to Tesseract OCR page rendering for scanned PDFs.
    """
    try:
        doc = fitz.open(pdf_path)
        full_text = []

        for page_num, page in enumerate(doc):
            text = page.get_text("text").strip()
            
            # If page text is very sparse (< 20 words) and OCR fallback is enabled
            words_count = len(text.split())
            if words_count < 20 and use_ocr_fallback and is_ocr_available():
                ocr_text = ocr_pdf_page(page)
                if len(ocr_text.split()) > words_count:
                    text = ocr_text

            # Clean up common PDF extraction noise
            clean_text = text.replace("\n\n", " ").replace("  ", " ").strip()
            if clean_text:
                full_text.append(clean_text)

        doc.close()
        combined = " ".join(full_text)

        if len(combined) < 50:
            return ""

        return combined

    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """Split text into overlapping chunks for RAG."""
    words = text.split()
    chunks = []

    if len(words) == 0:
        return chunks

    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.strip()) > 50:  # skip very short chunks
            chunks.append(chunk)

    return chunks