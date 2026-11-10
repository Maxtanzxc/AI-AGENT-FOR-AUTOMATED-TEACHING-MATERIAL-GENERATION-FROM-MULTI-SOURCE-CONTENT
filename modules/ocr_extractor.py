import io
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from config import IS_TESSERACT_AVAILABLE

def is_ocr_available() -> bool:
    """Return True if Tesseract OCR binary is configured and available."""
    return IS_TESSERACT_AVAILABLE

def extract_text_from_image(image_input, lang: str = "eng") -> str:
    """
    Extract text from an image (file path, bytes, or PIL.Image).
    Returns cleaned extracted text string.
    """
    if not IS_TESSERACT_AVAILABLE:
        print("Tesseract OCR is not available on this system.")
        return ""

    try:
        if isinstance(image_input, (str, bytes)):
            if isinstance(image_input, bytes):
                img = Image.open(io.BytesIO(image_input))
            else:
                img = Image.open(image_input)
        elif isinstance(image_input, Image.Image):
            img = image_input
        else:
            print("Unsupported image format for OCR.")
            return ""

        # Convert image to RGB if needed
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        text = pytesseract.image_to_string(img, lang=lang)
        cleaned_text = text.replace("\r\n", "\n").strip()
        return cleaned_text

    except Exception as e:
        print(f"OCR image extraction error: {e}")
        return ""

def ocr_pdf_page(page: fitz.Page, dpi: int = 150, lang: str = "eng") -> str:
    """
    Render a PyMuPDF PDF page into a high-resolution pixmap and run Tesseract OCR.
    """
    if not IS_TESSERACT_AVAILABLE:
        return ""

    try:
        # Render PDF page to pixmap
        pix = page.get_pixmap(dpi=dpi)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))

        text = pytesseract.image_to_string(img, lang=lang)
        cleaned_text = text.replace("\r\n", "\n").strip()
        return cleaned_text

    except Exception as e:
        print(f"OCR PDF page extraction error: {e}")
        return ""
