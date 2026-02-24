def recall_at_k(results, relevant, k=None):
    """
    Computes recall@k
    results: list of dicts with 'text' key or list of strings
    relevant: list of relevant keywords
    k: number of top results to consider
    """
    if k is None:
        k = len(results)
    if not results:
        return 0
    topk = results[:k]
    topk_texts = []
    for r in topk:
        if isinstance(r, dict):
            text = r.get("text", "")
        else:
            text = str(r)
        if text:
            topk_texts.append(text.lower())
    hits = sum(any(word.lower() in t for t in topk_texts) for word in relevant)
    return 1 if hits > 0 else 0


def precision_at_k(results, relevant, k=None):
    """
    Computes precision@k
    """
    if k is None:
        k = len(results)
    if not results:
        return 0
    topk = results[:k]
    topk_texts = []
    for r in topk:
        if isinstance(r, dict):
            text = r.get("text", "")
        else:
            text = str(r)
        if text:
            topk_texts.append(text.lower())
    if not topk_texts:
        return 0
    hits = sum(any(word.lower() in t for t in topk_texts) for word in relevant)
    return hits / len(topk_texts)


def context_overlap(results, relevant):
    """
    Simple context overlap score between top-k results and relevant keywords
    Returns fraction of relevant keywords present in top-k
    """
    topk_texts = []
    for r in results:
        if isinstance(r, dict):
            text = r.get("text", "")
        else:
            text = str(r)
        if text:
            topk_texts.append(text.lower())
    if not topk_texts:
        return 0
    matched = sum(1 for word in relevant if any(word.lower() in t for t in topk_texts))
    return matched / len(relevant)
