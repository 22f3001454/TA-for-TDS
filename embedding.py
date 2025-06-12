import os
import json
import uuid
import asyncio
import httpx
from typing import List

# Load AIProxy token from environment
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    raise EnvironmentError("Missing AIPROXY_TOKEN")

# Constants
EMBEDDING_URL = "https://aipipe.org/openai/v1/embeddings"
EMBEDDING_MODEL = "text-embedding-3-small"
OUTPUT_FILE = "vectors.json"

async def get_embedding(text: str) -> List[float]:
    headers = {
        "Authorization": f"Bearer {AIPROXY_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": EMBEDDING_MODEL,
        "input": text
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(EMBEDDING_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]

async def process_chunks(chunks_path):
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    results = []
    for chunk in chunks:
        text = chunk.get("content", "").strip()
        if not text:
            continue
        try:
            embedding = await get_embedding(text)
            results.append({
                "id": str(uuid.uuid4()),
                "embedding": embedding,
                "metadata": {
                    "text": text,
                    "source": "chunk",
                    "original_id": chunk.get("id", "")
                }
            })
        except Exception as e:
            print(f"Chunk skipped due to error: {e}")
    return results

async def process_threads(threads_path):
    with open(threads_path, "r", encoding="utf-8") as f:
        threads = json.load(f)

    results = []
    for thread in threads:
        title = thread.get("thread_title", "")
        for post in thread.get("posts", []):
            text = post.get("text", "").strip()
            if not text:
                continue
            try:
                embedding = await get_embedding(text)
                results.append({
                    "id": str(uuid.uuid4()),
                    "embedding": embedding,
                    "metadata": {
                        "text": text,
                        "source": "thread",
                        "thread_title": title,
                        "post_url": post.get("url"),
                        "created_by": post.get("created_by"),
                        "type": post.get("type")
                    }
                })
            except Exception as e:
                print(f"Post skipped due to error: {e}")
    return results

async def main():
    chunks_vectors = await process_chunks("chunks.json")
    threads_vectors = await process_threads("tds_threads.json")

    all_vectors = chunks_vectors + threads_vectors
    print(f"✅ Total vectors created: {len(all_vectors)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_vectors, f, indent=2)
    print(f"📁 Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
