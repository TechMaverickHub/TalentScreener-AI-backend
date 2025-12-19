from collections import defaultdict

from app.langchain_utils.vectorstore import get_vectorstore


def search_matching_documents(query_text: str, top_k: int = 5, filter_type: str = "resume"):
    vectorstore = get_vectorstore()

    results = vectorstore.similarity_search_with_score(query_text, k=top_k * 5)
    filtered = []

    for doc, score in results:
        if doc.metadata.get("type") != filter_type:
            continue

        filtered.append({
            "score": round(score, 3),
            "metadata": doc.metadata,
            "content": doc.page_content
        })

        if len(filtered) >= top_k:
            break

    return filtered


def search_matching_documents_new(query_text: str, top_k: int = 5, filter_type: str = "resume"):
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search_with_score(query_text, k=top_k * 10)

    job_scores = defaultdict(list)
    job_docs = {}

    for doc, score in results:
        if doc.metadata.get("type") != filter_type:
            continue

        job_id = doc.metadata.get("job_id") or doc.metadata.get("title")
        job_scores[job_id].append(score)
        if job_id not in job_docs:
            job_docs[job_id] = doc

    # Aggregate scores (mean or max)
    scored_jobs = sorted(
        ((job_id, sum(scores)/len(scores), job_docs[job_id]) for job_id, scores in job_scores.items()),
        key=lambda x: x[1],
        reverse=True
    )

    # Format top results
    top_results = []
    for job_id, score, doc in scored_jobs[:top_k]:
        top_results.append({
            "score": round(score, 3),
            "metadata": doc.metadata,
            "content": doc.page_content
        })

    return top_results


def search_matching_documents_new_2(
    query_text: str,
    top_k: int = 5,
    filter_type: str = "resume",
    score_threshold: float = 1.2,  # <<< NEW: filter weak matches
    include_titles: list[str] = None  # <<< NEW: optional title filter
):
    vectorstore = get_vectorstore()
    raw_results = vectorstore.similarity_search_with_score(query_text, k=top_k * 10)

    filtered = []

    for doc, score in raw_results:
        metadata = doc.metadata or {}

        # Filter by type
        if metadata.get("type") != filter_type:
            continue

        # Filter by optional allowed job titles (e.g. frontend/backend)
        if include_titles:

            job_title = (metadata.get("title") or "").lower()
            if not any(allowed.lower() in job_title for allowed in include_titles):
                continue

        # Filter out poor similarity scores
        if score > score_threshold:
            continue

        filtered.append({
            "score": round(score, 3),
            "metadata": metadata,
            "content": doc.page_content
        })

        if len(filtered) >= top_k:
            break

    return filtered
