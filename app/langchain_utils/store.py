from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.langchain_utils.vectorstore import get_vectorstore, FAISS_INDEX_PATH


def store_text(text: str, metadata: dict):
    vectorstore = get_vectorstore()

    #Chunking(optional)
    # splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    # chunks = splitter.split_text(text)
    # docs = [Document(page_content=chunk, metadata=metadata) for chunk in chunks]

    # vectorstore.add_documents(docs)


    doc = Document(page_content=text, metadata=metadata)
    vectorstore.add_documents([doc])

    vectorstore.save_local(FAISS_INDEX_PATH)
    return {"status": "stored", "metadata": metadata}