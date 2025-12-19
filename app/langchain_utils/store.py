from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.jobrole.utils import extract_relevant_sections_with_llm
from app.langchain_utils.vectorstore import get_vectorstore, FAISS_INDEX_PATH


def store_job_description(text: str, metadata: dict):
    vectorstore = get_vectorstore()

    #Chunking(optional)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    relevant_text = extract_relevant_sections_with_llm(text)
    chunks = splitter.split_text(relevant_text)
    # docs = [Document(page_content=chunk, metadata=metadata) for chunk in chunks]

    docs = []
    for i, chunk in enumerate(chunks):
        chunk_metadata = {
            **metadata,
            "chunk_index": i,
            "chunk_total": len(chunks)
        }
        docs.append(Document(page_content=chunk, metadata=chunk_metadata))

    vectorstore.add_documents(docs)


    # doc = Document(page_content=text, metadata=metadata)
    # vectorstore.add_documents([doc])

    vectorstore.save_local(FAISS_INDEX_PATH)
    return {"status": "stored", "metadata": metadata}