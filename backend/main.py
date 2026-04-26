"""
Backend API for Code Review Assistant using DeepSeek Coder via Ollama.

This FastAPI application analyzes code submitted by users and provides
feedback on potential bugs, code quality issues, and improvement suggestions
using the DeepSeek Coder model.
"""

from fastapi import FastAPI, Form
import requests
import json

app = FastAPI()
OLLAMA_TIMEOUT_SECONDS = 1800

OLLAMA_API_URL = "http://localhost:11434/api/generate"


def read_ollama_stream(response: requests.Response) -> str:
    """Read Ollama's streamed NDJSON chunks into one response string."""
    chunks = []
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        data = json.loads(line)
        chunks.append(data.get("response", ""))
        if data.get("done"):
            break
    return "".join(chunks).strip()


def call_ollama(payload: dict) -> str:
    """Call Ollama with streaming enabled so long local generations stay alive."""
    streamed_payload = {**payload, "stream": True}
    with requests.post(
        OLLAMA_API_URL,
        json=streamed_payload,
        timeout=(10, OLLAMA_TIMEOUT_SECONDS),
        stream=True,
    ) as response:
        response.raise_for_status()
        return read_ollama_stream(response)

@app.post("/review/")
def review_code(code: str = Form(...)):
    """
    Review the provided code for bugs, issues, and improvements.

    Args:
        code: The source code to review (from HTML form data)

    Returns:
        A dictionary containing the code review feedback
    """
    # Construct a prompt instructing the model to act as an expert reviewer
    # The prompt explicitly asks for bugs, quality issues, and improvements
    # This structured request helps the model provide actionable feedback
    prompt = (
        "You are an expert code reviewer. Analyze the following code "
        "for bugs, code quality issues, and suggest improvements:\n\n"
        f"{code}"
    )

    # Send the code review request to Ollama's local API.
    # The helper streams chunks from Ollama, then returns one complete review.
    result = call_ollama({
        "model": "deepseek-coder:6.7b",  # DeepSeek Coder with 6.7B parameters
        "prompt": prompt,                 # The formatted prompt with code to review
    })

    # Return the review feedback.
    return {"review": result}
