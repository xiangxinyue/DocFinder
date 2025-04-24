import faiss
import pickle
from sentence_transformers import SentenceTransformer

index = faiss.read_index("Database\wiki_index.faiss")

with open("Database\wiki_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)
titles = metadata["titles"]
texts = metadata["texts"]

model = SentenceTransformer("all-MiniLM-L6-v2")
model.max_seq_length = 512
