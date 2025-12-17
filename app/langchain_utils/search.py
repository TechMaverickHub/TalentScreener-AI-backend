from app.langchain_utils.vectorstore import get_vectorstore


def search_matching_documents(query_text: str, top_k: int = 5, filter_type: str = "resume"):
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search_with_score(query_text, k=top_k)
    filtered = [
    {
    "score": round(score, 3),
    "metadata": doc.metadata,
    "content": doc.page_content
    }
    for doc, score in results
    if doc.metadata.get("type") == filter_type
    ]
    return filtered