# chat with pdf

## Run locally

1. Clone the repository:
    ```
    git clone https://github.com/sachin-404/pdf-chat
    cd pdf-chat
    ```

2. Create a virtual environment:
    ```
    python -m venv venv
    source venv/bin/activate   # On Windows: venv\Scripts\activate
    ```

3. Install the dependencies:
    ```
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    - Create a `.env` file in the project root directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY=your_openai_api_key
    ```

5. Run the FastAPI application:
    ```
    fastapi dev main.py
    ```

6. Access the API:
    - The API will be available at http://127.0.0.1:8000/docs
    - Use /uploadfile/ endpoint to upload a PDF file
    - Use /query/ endpoint to ask questions related to the uploaded PDF
