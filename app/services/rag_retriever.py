import re
from collections import Counter


def tokenize(text: str) -> list:
    """
    Clean tokenization (lowercase, alphanumeric only).
    """
    return re.findall(r"\b\w+\b", text.lower())


def keyword_search(
    query: str,
    df,
    k: int = 5,
    column_weights: dict | None = None,
    exact_boost: float = 2.0
):
    """
    Weighted keyword-based RAG search with token scoring.
    Designed to complement FAISS semantic retrieval.
    """

    if df is None or df.empty:
        return []

    if not query or not query.strip():
        return []

    if column_weights is None:
        column_weights = {
            "title": 4,
            "narration": 5,
            "scene_text": 4,
            "tags": 3,
            "category": 3
        }

    query_tokens = tokenize(query)
    query_counter = Counter(query_tokens)

    scored_results = []

    for _, row in df.iterrows():

        total_score = 0

        for col, weight in column_weights.items():
            if col not in df.columns:
                continue

            text = str(row.get(col, ""))
            tokens = tokenize(text)
            token_counter = Counter(tokens)

            # Weighted token overlap
            overlap_score = sum(
                min(query_counter[w], token_counter[w])
                for w in query_counter
            )

            total_score += weight * overlap_score

            # Exact phrase boost
            if query.lower() in text.lower():
                total_score += weight * exact_boost

        if total_score > 0:
            row_dict = row.to_dict()
            row_dict["keyword_score"] = float(total_score)
            scored_results.append(row_dict)

    scored_results.sort(
        key=lambda x: x["keyword_score"],
        reverse=True
    )

    return scored_results[:k]
