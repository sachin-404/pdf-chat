import os
from fastapi import UploadFile
from .openai_client import client, vector_store

async def handle_file_upload(file: UploadFile):
    if file.content_type != 'application/pdf':
        return {"status_code": 400, "message": "Invalid file type. Only PDF files are accepted."}

    # Save the file temporarily
    file_location = f"temp_files/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    # Open the file and upload to OpenAI
    with open(file_location, "rb") as file_stream:
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=[file_stream]
        )

    # Clean up the temporary file
    os.remove(file_location)

    if file_batch.status != 'completed':
        return {"status_code": 500, "message": "File upload failed."}

    return {"filename": file.filename, "message": "File uploaded successfully.", "file_batch_status": file_batch.status}
