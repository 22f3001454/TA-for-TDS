from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import httpx
from typing import Optional
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print(os.getenv("OPENAI_API_KEY"))
# Constants
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

EMBEDDING_URL = "https://aipipe.org/openai/v1/embeddings"
CHAT_URL = "https://aipipe.org/openai/v1/chat/completions"
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "google/gemini-2.0-flash-lite-001"
QDRANT_COLLECTION = "tds_kb"

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# Initialize Qdrant client
client = QdrantClient(
    url="https://your-qdrant-url",  # Replace with your Qdrant URL
    api_key=QDRANT_API_KEY,
)

# Request payload
class QueryPayload(BaseModel):
    question: str
    image: Optional[str] = None  # Base64 image (optional)

# Function to get embedding
async def get_embedding(text: str):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"model": EMBEDDING_MODEL, "input": text}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(EMBEDDING_URL, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]

# Function to generate GPT answer
async def generate_gpt_answer(question: str, context: str):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    system_prompt = """
    You are a helpful assistant that answers academic and technical questions using the context provided.
    Guidelines:
    - `"answer"` should contain a concise and accurate response to the user's question.
    - Mention the specific model or tool version clearly if the question involves one.
    - If a numeric or exact-format answer is expected , retain the format strictly.
    - If a method, tool, or model is not available, clearly state that and suggest alternatives if applicable (e.g., “Podman is recommended, though Docker is acceptable”).
    - Never fabricate facts not grounded in the context.
    - Give the answer such that it clarify the doubts , if some specific tools is accessible then tell that.
    - If a tools,model  is acceptable state that explicity.
    - Answer the question on that clarify the specific doubts.
    - Clarifies the usage of that the particular tools/model asked.
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{context}"},
        {"role": "user", "content": f"Question: {question}"}
    ]
    payload = {"model": CHAT_MODEL, "messages": messages}
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(CHAT_URL, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

@app.post("/api")
async def query_api(payload: QueryPayload):
    question = payload.question.strip()
    if not question:
        return {"answer": "Invalid input: Question cannot be empty.", "links": []}

    # Step 1: Embed the question
    try:
        query_vector = await get_embedding(question)
        print("Embedding:", query_vector[:5])  # print first 5 floats
    except Exception as e:
        return {"answer": f"Embedding failed: {str(e)}", "links": []}

    # Step 2: Search top 5 similar chunks
    try:
        results = client.search(
            collection_name=QDRANT_COLLECTION,
            query_vector=query_vector,
            limit=5
        )
    except Exception as e:
        return {"answer": f"Qdrant search failed: {str(e)}", "links": []}

    if not results:
        return {"answer": "No relevant results found.", "links": []}

    # Step 3: Build full GPT context
    context_blocks = [r.payload.get("text", "") for r in results]
    print("Context blocks:", context_blocks)
    # Step 4: Build links from "source": "thread"
    links = []
    for r in results:
        metadata = r.payload
        if metadata.get("source") == "thread" and "post_url" in metadata:
            links.append({
                "url": metadata["post_url"],
                "text": metadata.get("text", "").strip().replace("\n", " ")
            })
    for r in results:
        print("Payload:", r.payload)

    # Step 5: Ask GPT with context
    full_context = "\n\n".join(context_blocks)
    try:
        gpt_answer = await generate_gpt_answer(payload.question, full_context)
    except Exception as e:
        return {"answer": f"GPT generation failed: {str(e)}", "links": links}

    return {
        "answer": gpt_answer.strip(),  
        "links": links
    }
