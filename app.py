from fastapi import FastAPI, UploadFile, File, Form
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

# Initialize the assistant
assistant = client.beta.assistants.create(
    name="Document Assistant",
    instructions="You are a knowledgeable assistant that helps users with questions related to the content of uploaded PDF documents. Use your understanding of the text within the provided files to answer queries accurately and thoroughly.",
    model="gpt-4o",
    tools=[{"type": "file_search"}],
)

# Update the assistant to use the vector store
assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

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

@app.post("/query/")
async def query_document(question: str = Form(...)):
    # Create a thread and attach the file to the message
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ]
    )

    # Use the create and poll SDK helper to create a run and poll the status of the run until it's in a terminal state
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )

    # Retrieve the messages from the thread
    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
    message_content = messages[0].content[0].text

    # Process annotations and citations
    annotations = message_content.annotations
    citations = []
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
        if file_citation := getattr(annotation, "file_citation", None):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f"[{index}] {cited_file.filename}")

    response = {
        "response": message_content.value,
        "citations": "\n".join(citations)
    }

    return JSONResponse(content=response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
