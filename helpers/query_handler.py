from .openai_client import client, assistant

async def handle_query(question: str):
    # Create a thread and attach the file to the message
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ]
    )

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

    return {"response": message_content.value}
