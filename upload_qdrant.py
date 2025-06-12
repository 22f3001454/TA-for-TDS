import os
import json
import httpx
import asyncio
from typing import List

# Qdrant settings
QDRANT_URL = "your-qdrant-url"  # Replace with your Qdrant URL
QDRANT_API_KEY = "your-qdrant-api-key"  # Replace with your Qdrant API key
COLLECTION_NAME = "tds_kb"

HEADERS = {
    "Authorization": f"Bearer {QDRANT_API_KEY}",
    "Content-Type": "application/json"
}

# ✅ Validate vector format before upload
def is_valid_qdrant_point(point):
    return (
        isinstance(point.get("id"), (str, int)) and
        isinstance(point.get("embedding"), list) and
        len(point["embedding"]) == 1536 and
        all(isinstance(x, float) for x in point["embedding"])
    )

# ✅ Upload one batch of points
async def upload_batch(points):
    url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points?wait=true"
    payload = {"points": points}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.put(url, headers=HEADERS, json=payload)
        r.raise_for_status()
        print(f"✅ Uploaded batch of {len(points)} points")

# ✅ Main upload flow
async def main():
    with open("vectors.json", "r", encoding="utf-8") as f:
        raw_vectors = json.load(f)

    qdrant_points = []

    # Validate and prepare
    for p in raw_vectors:
        if not is_valid_qdrant_point(p):
            print(f"⚠️ Skipped invalid vector: {p.get('id')}")
            continue
        qdrant_points.append({
            "id": p["id"],
            "vector": p["embedding"],
            "payload": p.get("metadata", {})
        })

    print(f"📦 Total valid vectors to upload: {len(qdrant_points)}")

    # Upload in small batches to avoid 413
    batch_size = 10
    for i in range(0, len(qdrant_points), batch_size):
        batch = qdrant_points[i:i + batch_size]
        print(f"⬆️ Uploading batch {i // batch_size + 1}")
        await upload_batch(batch)

    print("🎉 Upload complete!")

# 🚀 Run the script
if __name__ == "__main__":
    asyncio.run(main())
