from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Initialize the OpenAI client
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Create the vector store
vector_store = client.beta.vector_stores.create(name="File Data")

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        return JSONResponse(status_code=400, content={"message": "Invalid file type. Only PDF files are accepted."})

    # Save the file temporarily
    file_location = f"temp_files/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    # Open the file and upload to OpenAI
    with open(file_location, "rb") as file_stream:
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=[file_stream]
        )

    if file_batch.status != 'completed':
        return JSONResponse(status_code=500, content={"message": "File upload failed."})

    # Clean up the temporary file
    os.remove(file_location)

    return {"filename": file.filename, "message": "File uploaded successfully.", "file_batch_status": file_batch.status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
