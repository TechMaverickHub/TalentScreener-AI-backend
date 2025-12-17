import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.faiss import FAISS

FAISS_INDEX_PATH = "vectorstore/faiss_index"
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")



def get_vectorstore():
    if os.path.exists(FAISS_INDEX_PATH):
        return FAISS.load_local(FAISS_INDEX_PATH, embedding_model,allow_dangerous_deserialization=True)
    else:
        return FAISS.from_texts(["placeholder"], embedding_model)
