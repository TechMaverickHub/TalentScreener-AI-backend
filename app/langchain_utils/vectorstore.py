import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.faiss import FAISS

FAISS_INDEX_PATH = "vectorstore/faiss_index"

#Embedding model
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")



def get_vectorstore():
    if os.path.exists(FAISS_INDEX_PATH):

        # Load the vectorstore
        return FAISS.load_local(FAISS_INDEX_PATH, embedding_model,allow_dangerous_deserialization=True)
    else:
        return FAISS.from_texts(["placeholder"], embedding_model)


def safe_vector_format(vec):
    if hasattr(vec, "tolist"):
        return vec.tolist()
    if isinstance(vec, list):
        return vec
    raise ValueError("Unexpected vector format")

