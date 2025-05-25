from langchain_community.document_loaders import PyPDFLoader
from pdf2image import convert_from_path
import pytesseract
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

def ocr_batch(args):
    batch_pages, pdf_path, total_pages = args
    results = []
    for page_num in batch_pages:
        page = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)[0]
        text = pytesseract.image_to_string(page, lang='vie+eng')
        results.append({"page_content": text, "metadata":
            {"page": page_num, "source": pdf_path, "total_pages": total_pages}})
    return results

def load_document_with_ocr(pdf_path, batch_size=10):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()  # Load tất cả văn bản từ PDF (nếu có)

    total_pages = len(documents)
    print(f"Tổng số trang: {total_pages}")

    # Tách trang có text và không có text
    documents_with_text = []
    pages_to_ocr = []
    for doc in documents:
        text = doc.page_content.strip() if doc.page_content else ""
        page_num = doc.metadata.get('page', 0)
        if text:
            documents_with_text.append({"page_content": text, "metadata":
                {"page": page_num, "source": pdf_path, "total_pages": total_pages}})
        else:
            pages_to_ocr.append(page_num)

    print(f"Trang có sẵn text: {len(documents_with_text)}, cần OCR: {len(pages_to_ocr)}")

    # Chia batch OCR
    batches = [pages_to_ocr[i:i+batch_size] for i in range(0, len(pages_to_ocr), batch_size)]

    # Progress bar với multiprocessing
    with Pool(processes=cpu_count()) as pool:
        with tqdm(total=len(batches), desc="Đang OCR", unit="batch") as pbar:
            for batch_result in pool.imap_unordered(ocr_batch, [(batch, pdf_path, total_pages) for batch in batches]):
                documents_with_text.extend(batch_result)
                pbar.update(1)

    # Sắp xếp kết quả theo thứ tự trang
    documents_with_text.sort(key=lambda x: x['metadata']['page'])
    return documents_with_text
