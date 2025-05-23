from pdf2image import convert_from_bytes
from language_detection import *
import pytesseract

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
# print(f"Detected Language: {detected_lang}")
# print(f"Extracted Text: {text}")