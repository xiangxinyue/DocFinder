import os
import gdown
#added comment for deployment

def download_file(file_id, output_path):
    if not os.path.exists(output_path):
        print(f"Downloading {output_path} from Google Drive")
        gdown.download(id=file_id, output=output_path, quiet=False)
    else:
        print(f"{output_path} already exists, skipping download.")

def setup_database():
    os.makedirs("Database", exist_ok=True)

    index_file_id = "1OJe2t4SZRNzUAUYWoVtTyXtUSFzXDyL6"
    metadata_file_id = "1Op06GqoKs24YgH_phckH5w4R4H7bz4eX"

    download_file(index_file_id, "Database/wiki_index.faiss")
    download_file(metadata_file_id, "Database/wiki_metadata.pkl")

setup_database()

from fastapi import FastAPI
from pydantic import BaseModel
from Search.semantic_search import semantic_search  

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://doc-finder-ecru.vercel.app",
        "https://doc-finder-git-main-havewaveteam12.vercel.app",
        "https://doc-finder-8ftcgmeom-havewaveteam12.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "Backend is up"}
    
class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def query(request: QueryRequest):
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000)) 
    uvicorn.run("main:app", host="0.0.0.0", port=port)

