from langchain_core.documents import Document

from app.langchain_utils.vectorstore import get_vectorstore, FAISS_INDEX_PATH


def store_text(text: str, metadata: dict):
    vectorstore = get_vectorstore()
    doc = Document(page_content=text, metadata=metadata)
    vectorstore.add_documents([doc])
    vectorstore.save_local(FAISS_INDEX_PATH)
    return {"status": "stored", "metadata": metadata}