from app.core.models import RAGQuery
from app.services.rag_retriever import keyword_search
from app.services.faiss_retriever import faiss_search


def normalize_scores(results, score_key):
    """
    Normalize scores to 0–1 range.
    """
    if not results:
        return results

    scores = [r.get(score_key, 0.0) for r in results]
    min_s, max_s = min(scores), max(scores)

    if max_s == min_s:
        for r in results:
            r[f"{score_key}_norm"] = 1.0
        return results

    for r in results:
        r[f"{score_key}_norm"] = (
            (r.get(score_key, 0.0) - min_s) / (max_s - min_s)
        )

    return results


def hybrid_merge(semantic, keyword, alpha=0.65):
    """
    Merge semantic + keyword results.
    alpha = weight for semantic
    """

    semantic = normalize_scores(semantic, "score")
    keyword = normalize_scores(keyword, "keyword_score")

    merged = {}

    # Add semantic
    for r in semantic:
        key = r.get("scene_number") or r.get("text")
        merged[key] = r
        merged[key]["final_score"] = alpha * r.get("score_norm", 0)

    # Merge keyword
    for r in keyword:
        key = r.get("scene_number") or r.get("text")

        if key not in merged:
            merged[key] = r
            merged[key]["final_score"] = 0

        merged[key]["final_score"] += (
            (1 - alpha) * r.get("keyword_score_norm", 0)
        )

    results = list(merged.values())
    results.sort(key=lambda x: x["final_score"], reverse=True)

    return results


def retrieve_context(
    req: RAGQuery,
    df,
    model,
    index,
    mode: str = "hybrid"
):
    """
    Unified RAG retrieval adapter.

    Modes:
    - faiss
    - keyword
    - hybrid (recommended)
    """

    if not req.query:
        return []

    k = req.k or 5

    if mode == "faiss":
        return faiss_search(
            query=req.query,
            df=df,
            model=model,
            index=index,
            k=k
        )

    if mode == "keyword":
        return keyword_search(
            query=req.query,
            df=df,
            k=k
        )

    # ==========================
    # HYBRID MODE
    # ==========================
    semantic_results = faiss_search(
        query=req.query,
        df=df,
        model=model,
        index=index,
        k=k * 2  # fetch extra for merge
    )

    keyword_results = keyword_search(
        query=req.query,
        df=df,
        k=k * 2
    )

    if not semantic_results and not keyword_results:
        return []

    if not semantic_results:
        return keyword_results[:k]

    if not keyword_results:
        return semantic_results[:k]

    merged = hybrid_merge(semantic_results, keyword_results)

    return merged[:k]
