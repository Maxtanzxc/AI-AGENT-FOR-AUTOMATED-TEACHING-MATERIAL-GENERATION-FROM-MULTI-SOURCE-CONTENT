from PIL import Image, ImageDraw, ImageFont
import os
import tempfile
from modules.ocr_extractor import extract_text_from_image, is_ocr_available
from modules.pdf_extractor import extract_text_from_pdf, chunk_text

print(f"Is Tesseract OCR available? {is_ocr_available()}")

# Create a sample image with clear text
img = Image.new('RGB', (600, 150), color=(255, 255, 255))
d = ImageDraw.Draw(img)
text_content = "EduForge AI Tesseract OCR Verification Test"
d.text((20, 50), text_content, fill=(0, 0, 0))

tmp_img_path = tempfile.mktemp(suffix=".png")
img.save(tmp_img_path)

try:
    extracted = extract_text_from_image(tmp_img_path)
    print(f"Image OCR Extracted Result: '{extracted}'")
    assert "EduForge" in extracted or "Tesseract" in extracted or "Verification" in extracted or "OCR" in extracted, "OCR text did not match expected tokens"
    print("SUCCESS: Image OCR test passed!")
finally:
    if os.path.exists(tmp_img_path):
        os.remove(tmp_img_path)
