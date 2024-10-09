from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
from pydantic import BaseModel
from engine.search_engine import SearchEngine
import random

# Create the FastAPI app
app = FastAPI()

# Initialize your search engine
search_engine = SearchEngine()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ballharbor.vercel.app", "http://localhost:3000"],  # Specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


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

        # Check if results is not None and has the expected attributes
        if results is None or results.empty:
            return {"query": request.query, "data": []}

        # Convert the entire DataFrame to a list of dictionaries
        data = results.to_dict(orient='records')
        return {"query": request.query, "data": data}
    except Exception as e:
        # Catch and log any unexpected errors
        return {"error": f"An error occurred: {str(e)}"}

# Endpoint to handle random example query (just as a test)
@app.get("/random")
def random_query():
    try:
        # Define example queries for testing
        example_queries = [
            "Lebron James driving layups",
            "Wembanyama fadeaways"
        ]

        # Select a random example query
        query = random.choice(example_queries)
        
        # Run the search engine's query function
        results = search_engine.query(query)

        # Check if results is not None and has the expected attributes
        if results is None or results.empty:
            return {"query": query, "data": []}

        # Convert the entire DataFrame to a list of dictionaries
        data = results.to_dict(orient='records')
        return {"query": query, "data": data}
    except Exception as e:
        # Catch and handle any errors during processing
        return {"error": f"An error occurred: {str(e)}"}
    
# Endpoint to handle random example query (just as a test)
@app.get("/error")
def random_query():
    try:
        # Define example queries for testing
        example_queries = [
            "Dejounte Murray floaters",
        ]

        # Select a random example query
        query = random.choice(example_queries)
        
        # Run the search engine's query function
        results = search_engine.query(query)

        # Check if results is not None and has the expected attributes
        if results is None or results.empty:
            return {"query": query, "data": []}

        # Convert the entire DataFrame to a list of dictionaries
        data = results.to_dict(orient='records')
        return {"query": query, "data": data}
    except Exception as e:
        # Catch and handle any errors during processing
        return {"error": f"An error occurred: {str(e)}"}


# Run the FastAPI server when this file is executed as a script
if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)