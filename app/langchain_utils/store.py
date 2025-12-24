from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.jobrole.utils import extract_relevant_sections_with_llm
from app.langchain_utils.vectorstore import get_vectorstore, FAISS_INDEX_PATH

def store_job_description(text: str, metadata: dict):
    # 🔹 Load or initialize the FAISS vector store
    vectorstore = get_vectorstore()

    # 🔸 Step 1: Extract the most relevant sections using an LLM
    # This cleans and condenses the input to just what matters for semantic search
    relevant_text = extract_relevant_sections_with_llm(text)

    # 🔸 Step 2: Chunk the relevant text for better granularity during search
    # RecursiveCharacterTextSplitter ensures overlapping chunks to preserve context across boundaries
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(relevant_text)

    # docs = [Document(page_content=chunk, metadata=metadata) for chunk in chunks]

    # 🔸 Step 3: Create Document objects from chunks with metadata
    # Each chunk is assigned index metadata to help with tracking and reconstruction
    docs = []
    for i, chunk in enumerate(chunks):
        chunk_metadata = {
            **metadata,
            "chunk_index": i,           # Position of this chunk
            "chunk_total": len(chunks)  # Total chunks for the job
        }
        docs.append(Document(page_content=chunk, metadata=chunk_metadata))

    # 🔸 Step 4: Embed and index the documents into FAISS
    # This will allow fast vector similarity search later during retrieval
    vectorstore.add_documents(docs)

    # doc = Document(page_content=text, metadata=metadata)
    # vectorstore.add_documents([doc])

    # 🔸 Step 5: Persist the updated FAISS index to disk
    # Ensures the vectors are available across restarts
    vectorstore.save_local(FAISS_INDEX_PATH)

    return {"status": "stored", "metadata": metadata}
