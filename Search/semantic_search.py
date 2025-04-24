import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer

def load_index_and_metadata():
    index_path = "Database/wiki_index.faiss"
    metadata_path = "Database/wiki_metadata.pkl"

    if not os.path.exists(index_path) or not os.path.exists(metadata_path):
        raise FileNotFoundError("FAISS index or metadata file not found. Run setup_data.py first.")

    index = faiss.read_index(index_path)

    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)

    return index, metadata["titles"], metadata["texts"]

def load_model():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    model.max_seq_length = 512
    return model

def generate_source_url(title):
    return f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"

#main search function
def semantic_search(query, top_k=5):
    index, titles, texts = load_index_and_metadata()
    model = load_model()

    query_embedding = model.encode([query], normalize_embeddings=True)
    scores, indices = index.search(query_embedding, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        title = titles[idx]
        text = texts[idx]
        score = f"{round(float(scores[0][i]) * 100, 2)}%"
        source_url = generate_source_url(title)

        results.append({
            "title": title,
            "text": text,
            "score": score,
            "source": source_url
        })

    return {"matches": results}
