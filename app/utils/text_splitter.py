from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
from .pdf_loader import load_document_with_ocr
from langchain.schema import Document

def split_documents_into_chunks(pdf, chunk_size=1024, chunk_overlap=200):
    # Split data to chunks
    raw_docs = load_document_with_ocr(pdf)
    documents = [Document(page_content=d["page_content"], metadata=d["metadata"]) for d in raw_docs]


    text_spliter = RecursiveCharacterTextSplitter(
        separators=[
            "\n\n",
            "\n",
            " ",
            ".",
            ",",
            "\u200b",  # Zero-width space
            "\uff0c",  # Fullwidth comma
            "\u3001",  # Ideographic comma
            "\uff0e",  # Fullwidth full stop
            "\u3002",  # Ideographic full stop
        ],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    texts = text_spliter.split_documents(documents)

    subpage = 0
    page_init = -1
    for text in texts:
        if (text.metadata["page"] == page_init):
            subpage += 1
            text.metadata["subpage"] = subpage
        else:
            subpage = 0
            text.metadata["subpage"] = 0
            page_init += 1

    for text in texts:
        text.page_content = re.sub(r"\n", " ", text.page_content)

    return texts
