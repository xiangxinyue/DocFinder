import os
import faiss
import pickle
import requests
import threading
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# ========== Setup Database ==========
def download_file(url, output_path):
    try:
        if not os.path.exists(output_path):
            print(f"Downloading {output_path} from GitHub Releases")
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"{output_path} downloaded successfully.")
            else:
                print(f"Failed to download {url}, status code: {response.status_code}")
        else:
            print(f"{output_path} already exists, skipping download.")
    except Exception as e:
        print(f"Error downloading file: {str(e)}")

def setup_database():
    try:
        os.makedirs("Database", exist_ok=True)
        index_url = "https://github.com/xiangxinyue/DocFinder/releases/download/release/wiki_index.faiss"
        metadata_url = "https://github.com/xiangxinyue/DocFinder/releases/download/release/wiki_metadata.pkl"
        download_file(index_url, "Database/wiki_index.faiss")
        download_file(metadata_url, "Database/wiki_metadata.pkl")
        print("Database setup complete")
    except Exception as e:
        print(f"Error setting up database: {str(e)}")

def load_index_and_metadata():
    index_path = "Database/wiki_index.faiss"
    metadata_path = "Database/wiki_metadata.pkl"

    if not os.path.exists(index_path) or not os.path.exists(metadata_path):
        raise FileNotFoundError("FAISS index or metadata file not found.")

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

def semantic_search(query, top_k=5):
    global index, titles, texts, model

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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://doc-finder-ecru.vercel.app",
        "https://doc-finder-havewaveteam12.vercel.app",
        "http://doc-finder-git-main-havewaveteam12.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Global error: {str(exc)}")
    return JSONResponse(status_code=500, content={"message": f"Internal server error: {str(exc)}"})

@app.get("/")
async def root():
    return {"status": "Backend is up"}

@app.head("/")
async def head_root():
    return {"status": "Backend is up"}

@app.options("/query")
async def options_query():
    return {}

@app.get("/health")
async def health():
    return {"status": "healthy"}

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def query(request: QueryRequest):
    try:
        print(f"Processing query: {request.query}")
        return semantic_search(request.query, top_k=5)
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        raise


def init():
    global index, titles, texts, model
    setup_database()
    index, titles, texts = load_index_and_metadata()
    model = load_model()
    print("Model and FAISS index loaded")

startup_thread = threading.Thread(target=init)
startup_thread.daemon = True
startup_thread.start()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port)
