from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
from .pdf_loader import load_document
def split_documents_into_chunks(pdf, chunk_size=512, chunk_overlap=100):
    # Split data to chunks
    documents = load_document(pdf)
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
            "",
        ],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    texts = text_spliter.split_documents(documents)

    # Add subpage to track down the paragraph in page
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
        # Remove /n in text
        text.page_content = re.sub(r"\n", " ", text.page_content)

    # print(len(texts))
    # print(len(documents))
    # for doc in documents:
    #     print(doc.metadata)
    return texts
