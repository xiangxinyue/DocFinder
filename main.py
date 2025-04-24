from fastapi import FastAPI
from pydantic import BaseModel
from Search.semantic_search import nn_search  

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def query(request: QueryRequest):
    num_index, score, index, sentence_decoder, title_decoder = nn_search(
        texts=[request.query], n_neighbors=5, load_title_decoder=True
    )

    results = []
    for i in range(5):
        idx = index[0][i]
        nid = num_index[0][i]
        results.append({
            "text": sentence_decoder[nid][idx],
            "title": title_decoder[nid][idx],
            "score": float(score[0][i]),
            "source": f"https://example.com/{title_decoder[nid][idx]}" 
        })
    return {"matches": results}
