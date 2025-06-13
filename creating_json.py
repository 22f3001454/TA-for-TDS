import os
import json
from pathlib import Path
import tiktoken
import re
# Configuration
MODEL = "gpt-4o"            # OpenAI model used to determine tokenizer
TOKEN_LIMIT = 4096          # Max tokens per chunk
INPUT_DIR = "."             # Root directory to search for .md files
OUTPUT_FILE = "chunks.json" # Output JSON file

def split_markdown(text, max_tokens=TOKEN_LIMIT, model=MODEL):
    enc = tiktoken.encoding_for_model(model)
    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""
    current_tokens = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        tokens = len(enc.encode(para))
        if current_tokens + tokens > max_tokens:
            chunks.append(current_chunk.strip())
            current_chunk = para
            current_tokens = tokens
        else:
            current_chunk += "\n\n" + para
            current_tokens += tokens

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

def main():
    all_chunks = []
    for path in Path(INPUT_DIR).rglob("*.md"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Skipped {path}: {e}")
            continue

        chunks = split_markdown(content)
        for idx, chunk in enumerate(chunks):
            id=f"{path}#{idx}"
            if id:
                try:
                    # Normalize slashes (\\ to /)
                    path = id.replace("\\", "/")

                    # Extract just the filename
                    filename = os.path.basename(path)              # "embeddings.md#0"
                    base = re.sub(r"\.md.*$", "", filename)        # remove .md and anything after it

                    # Construct final URL
                    url = f"https://tds.s-anand.net/#/{base}"
                except Exception as e:
                    print(f"Error processing {id}: {e}")
            all_chunks.append({
                "id": f"{path}#{idx}",
                "content": chunk,
                "url":url
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(all_chunks, out, indent=2, ensure_ascii=False)

    print(f"✅ Done! {len(all_chunks)} chunks written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
