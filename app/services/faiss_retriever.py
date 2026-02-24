import numpy as np


def faiss_search(
    query: str,
    df,
    model,
    index,
    k: int = 5,
    normalize: bool = True,
    min_score: float = 0.3,   # 🔥 similarity threshold
    diversify_by_title: bool = False
):
    """
    Perform FAISS similarity search.

    Returns top-k relevant chunks with metadata.
    """

    if not query or not query.strip():
        return []

    query_vec = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=normalize
    ).astype("float32")

    scores, indices = index.search(query_vec, k)

    results = []
    seen_titles = set()

    for score, idx in zip(scores[0], indices[0]):

        if idx < 0 or idx >= len(df):
            continue

        if score < min_score:
            continue  # 🔥 filter weak matches

        row = df.iloc[int(idx)]

        title = str(row.get("title", "")).strip()

        if diversify_by_title and title in seen_titles:
            continue

        seen_titles.add(title)

        chunk_text = row.get("chunk_text") or row.get("text", "")

        if not chunk_text or str(chunk_text).strip().lower() == "nan":
            continue

        results.append({
            "chunk_text": str(chunk_text).strip(),  # 🔥 use chunk_text
            "title": title,
            "month": row.get("month"),
            "category": row.get("category"),
            "scene_number": row.get("scene_number"),
            "score": float(score)
        })

    # Explicit sort (descending similarity)
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results
