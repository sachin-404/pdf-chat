from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from helpers.file_handler import handle_file_upload
from helpers.query_handler import handle_query

app = FastAPI()

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    response = await handle_file_upload(file)
    return JSONResponse(status_code=response.get("status_code", 200), content=response)

@app.post("/query/")
async def query_document(question: str = Form(...)):
    response = await handle_query(question)
    return JSONResponse(content=response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
