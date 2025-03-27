from PIL import Image
from pdf2image import convert_from_bytes
import pytesseract
from langdetect import detect
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def detectLang(pdf_bytes):
    images = convert_from_bytes(pdf_bytes)
    
    # Trích xuất text từ 1-2 trang đầu để phát hiện ngôn ngữ
    sample_text = ""
    for i, image in enumerate(images[:2]):  # Chỉ lấy 1-2 trang đầu
        sample_text += pytesseract.image_to_string(image)
    lang = detect(sample_text) if sample_text.strip() else "unknown"
    
    #map ngôn ngữ từ langdetect sang pytesseract
    lang_map = {
        'en': 'eng',
        'ja': 'jpn',
        'vi': 'vie',
    }
    tesseract_lang = lang_map.get(lang[:2], 'eng')
    return tesseract_lang

def pdfBytesToText(pdf_bytes):
    images = convert_from_bytes(pdf_bytes)
        
    lang = detectLang(pdf_bytes)
    
    texts = ""
    for i, image in enumerate(images):
        texts += pytesseract.image_to_string(image, lang=lang)
    
    return texts, lang

with open("app/assest/pdf/main.pdf", "rb") as f:
    pdf_bytes = f.read()

text, detected_lang = pdfBytesToText(pdf_bytes)
print(f"Detected Language: {detected_lang}")
print(f"Extracted Text: {text}")
