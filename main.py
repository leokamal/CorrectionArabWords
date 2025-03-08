from fastapi import FastAPI, File, UploadFile, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from correction_words_service import generate_query


# Initialize FastAPI app
app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for your specific needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for request body validation
class PromptRequest(BaseModel):
    selected_options: List[int]  # List of selected options
    text: str  # Input text to be processed


 # Hello World endpoint
@app.get("/hello")
async def hello_world():
    return {"message": "Hello, World!"}

# Query the database endpoint
@app.post("/query/")
def query_database_endpoint(request: PromptRequest):
    try:
        # Validate the input
        if not request.text:
            raise HTTPException(status_code=400, detail="Text is required")
        if not request.selected_options:
            raise HTTPException(status_code=400, detail="Selected options are required")
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": str(e)})
    # Generate the prompt based on user input
    output = generate_query(request.selected_options, request.text)
    return {"output": output}


# To start FastAPI, use: uvicorn main:app --reload