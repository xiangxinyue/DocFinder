import os
import requests
import threading
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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

# ========== Initialize FastAPI ==========
app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Global error: {str(exc)}")
    return JSONResponse(status_code=500, content={"message": f"Internal server error: {str(exc)}"})

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

db_thread = threading.Thread(target=setup_database)
db_thread.daemon = True
db_thread.start()

# ========== Load Semantic Search ==========
from sentence_transformers import SentenceTransformer
import pickle
import faiss
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index("Database/wiki_index.faiss")
with open("Database/wiki_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

def semantic_search(query: str, top_k: int = 5):
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for i in range(top_k):
        idx = indices[0][i]
        results.append({
            "text": metadata[idx]['text'],
            "title": metadata[idx]['title'],
            "score": float(distances[0][i]),
            "source": metadata[idx]['url']
        })

    return {"matches": results}

# ========== Define Query Endpoint ==========
class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def query(request: QueryRequest):
    try:
        print(f"Processing query: {request.query}")
        results_raw = semantic_search(request.query, top_k=5)
        results = []
        for match in results_raw["matches"]:
            results.append({
                "text": match["text"],
                "title": match["title"],
                "score": match["score"],
                "url": match["source"]
            })
        return {"matches": results}
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        raise

# ========== Local Development ==========
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port)
