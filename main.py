from fastapi import FastAPI,  HTTPException,  UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import tempfile
import os
import tempfile
from correction_words_service import generate_query
from file_processing import save_temp_file, process_and_save, read_file_content


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

# Read file content
@app.post("/read-file/")
async def process_file( file: UploadFile = File(...)):
    """Uploads a file and read file content."""
    try:
        temp_file_path = save_temp_file(file)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})

    # background_tasks.add_task(process_and_save, temp_file_path, selected_options)
    
    return {"content": read_file_content(temp_file_path)}

# Process file upload
@app.post("/process-file/")
async def process_file(background_tasks: BackgroundTasks, file: UploadFile = File(...), selected_options: List[int] = [0]):
    """Uploads a file, processes it in the background, and saves a corrected version."""
    try:
        temp_file_path = save_temp_file(file)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})

    # background_tasks.add_task(process_and_save, temp_file_path, selected_options)
    
    return {"message": process_and_save(temp_file_path, selected_options)}

# Download corrected file
@app.get("/download-file/")
async def download_file(filename: str):
    """Provides download access to the corrected file."""
    file_path = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, filename=filename)

# To start FastAPI, use: uvicorn main:app --reload