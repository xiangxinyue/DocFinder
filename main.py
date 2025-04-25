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
from fastapi.middleware.cors import CORSMiddleware
import os
# Import your search function
from Search.semantic_search import semantic_search

# Create FastAPI app first
app = FastAPI()

# Add a global exception handler to catch and log all errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Global error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"message": f"Internal server error: {str(exc)}"},
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Most permissive config, allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Define routes
@app.get("/")
async def root():
    return {"status": "Backend is up"}

@app.head("/")
async def head_root():
    # Support HEAD requests
    return {"status": "Backend is up"}

@app.options("/query")
async def options_query():
    # Explicitly handle OPTIONS preflight requests
    return {}

# Database setup functions
def download_file(file_id, output_path):
    try:
        if not os.path.exists(output_path):
            print(f"Downloading {output_path} from Google Drive")
            gdown.download(id=file_id, output=output_path, quiet=False)
        else:
            print(f"{output_path} already exists, skipping download.")
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        # Don't let it interrupt app startup
        pass

def setup_database():
    try:
        os.makedirs("Database", exist_ok=True)

        index_file_id = "1OJe2t4SZRNzUAUYWoVtTyXtUSFzXDyL6"
        metadata_file_id = "1Op06GqoKs24YgH_phckH5w4R4H7bz4eX"

        download_file(index_file_id, "Database/wiki_index.faiss")
        download_file(metadata_file_id, "Database/wiki_metadata.pkl")
        print("Database setup complete")
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        # Don't let it interrupt app startup
        pass

# Set up database in a separate thread, don't block app startup
import threading
db_thread = threading.Thread(target=setup_database)
db_thread.daemon = True  # Set as daemon thread, doesn't block app exit
db_thread.start()

# Query model
class QueryRequest(BaseModel):
    query: str

# Import search function, delayed import only when needed
@app.post("/query")
async def query(request: QueryRequest):
    try:
        # Delayed import to ensure app has started
        from Search.semantic_search import semantic_search
        
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
        raise  # Let the global exception handler deal with this error

# Add health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port)