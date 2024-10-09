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

        # Check if results is not None and has the expected attribute
        if results is None or not hasattr(results, 'Video_Link'):
            return {"query": request.query, "urls": []}

        # Convert the 'Video_Link' column to a list safely
        video_urls = results.Video_Link.values.tolist() if not results.Video_Link.empty else []

        # Stringify the URLs list to avoid JSON serialization issues
        stringified_urls = json.dumps(video_urls)
        return {"query": request.query, "urls": stringified_urls}
    except Exception as e:
        # Catch and log any unexpected errors
        return {"error": f"An error occurred: {str(e)}"}

# Endpoint to handle random example query (just as a test)
@app.get("/random")
def random_query():
    try:
        # Define example queries for testing
        example_queries = [
            "Dejounte Murray floaters"
        ]

        # Select a random example query
        query = random.choice(example_queries)
        
        # Run the search engine's query function
        results = search_engine.query(query)

        # Check if results is not None and has the expected attribute
        if results is None or not hasattr(results, 'Video_Link'):
            return {"query": query, "urls": []}

        # Convert the 'Video_Link' column to a list safely
        video_urls = results.Video_Link.values.tolist() if not results.Video_Link.empty else []

        # Return the formatted response
        return {"query": query, "urls": video_urls}
    except Exception as e:
        # Catch and handle any errors during processing
        return {"error": f"An error occurred: {str(e)}"}

# Run the FastAPI server when this file is executed as a script
if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)