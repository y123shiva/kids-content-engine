import faiss
import pandas as pd
import numpy as np
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer


def build_faiss_index(csv_path, index_path, model_name):

    csv_path = Path(csv_path)
    index_path = Path(index_path)

    df = pd.read_csv(csv_path)

    if "chunk_text" not in df.columns:
        raise ValueError("Dataset missing required 'chunk_text' column")

    texts = df["chunk_text"].fillna("").tolist()

    model = SentenceTransformer(model_name)

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,  # cosine compatibility
        show_progress_bar=True
    ).astype("float32")

    dimension = embeddings.shape[1]

    # Cosine similarity via inner product
    base_index = faiss.IndexFlatIP(dimension)
    index = faiss.IndexIDMap(base_index)

    ids = np.arange(len(embeddings)).astype("int64")
    index.add_with_ids(embeddings, ids)

    index_path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_path))

    # 🔥 Save metadata mapping
    metadata_path = index_path.with_suffix(".meta.json")

    metadata = {
        "model_name": model_name,
        "dimension": dimension,
        "total_vectors": len(embeddings),
        "source_csv": str(csv_path.name)
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return {
        "total_vectors": len(embeddings),
        "dimension": dimension,
        "model_name": model_name
    }
