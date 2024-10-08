from fastapi import FastAPI
from pydantic import BaseModel
from engine.search_engine import SearchEngine  # Import your search engine class
import random
import json
# Create the FastAPI app
app = FastAPI()

# Initialize your search engine
search_engine = SearchEngine()

# Define a request body schema using Pydantic
class QueryRequest(BaseModel):
    query: str

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the NBA Search Engine API"}

# Endpoint to handle queries
@app.post("/query")
def get_results(request: QueryRequest):
    try:
        # Run the search engine's query function
        results = search_engine.query(request.query)
        video_urls = results.Video_Link.values.tolist()
        stringified_urls = json.dumps(video_urls)
        return {"query": request.query, "urls": stringified_urls}
    except Exception as e:
        return {"error": str(e)}

# Endpoint to handle random example query (just as a test)
@app.get("/random")
def random_query():
    example_queries = ["Luka Doncic driving floaters in the playoffs", "Lebron James playoff clutch bricks", "Wembanyama fadeaways"]
    query = random.choice(example_queries)
    results = search_engine.query(query)
    video_urls = results.Video_Link.values.tolist()
    stringified_urls = json.dumps(video_urls)
    return {"query": query, "urls": video_urls}

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)