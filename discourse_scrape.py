import requests
import json
import time
import os
import base64
from bs4 import BeautifulSoup
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0"
}

cookies = {
    "_forum_session": "replace this with your session cookie",
    "_t": "replace this with your _t cookie"
}

BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
CATEGORY_URL = f"{BASE_URL}/c/courses/tds-kb/34"

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 4, 14)
os.makedirs("images", exist_ok=True)

def get_post_type(post, idx):
    if idx == 0:
        return "question"
    if "reply_to_post_number" in post and post["reply_to_post_number"] == 1:
        return "answer"
    return "follow-up"

def clean_html(content, post_url):
    soup = BeautifulSoup(content, "html.parser")
    images_base64 = []

    for img in soup.find_all("img"):
        if "emoji" in img.get("class", []) or "avatar" in img.get("class", []):
            img.decompose()
            continue

        src = img.get("src")
        try:
            res = requests.get(src, headers=headers, cookies=cookies)
            if res.status_code == 200:
                data = res.content
                img_name = os.path.basename(src.split("?")[0])
                img_path = os.path.join("images", img_name)
                with open(img_path, "wb") as f:
                    f.write(data)
                b64 = base64.b64encode(data).decode("utf-8")
                images_base64.append(b64)
                img.replace_with(f"[Image: {img_name}]")
        except Exception:
            img.decompose()

    text = soup.get_text(separator="\n").strip()
    return text, images_base64

def fetch_thread(topic_id, slug):
    url = f"{BASE_URL}/t/{slug}/{topic_id}.json"
    r = requests.get(url, headers=headers, cookies=cookies)
    if r.status_code != 200:
        return None

    data = r.json()
    posts = data["post_stream"]["posts"]
    thread_data = {
        "thread_title": data["title"],
        "thread_url": f"{BASE_URL}/t/{slug}/{topic_id}",
        "posts": []
    }

    for idx, post in enumerate(posts):
        text, images_b64 = clean_html(post["cooked"], f"{BASE_URL}/t/{slug}/{topic_id}/{post['post_number']}")
        thread_data["posts"].append({
            "type": get_post_type(post, idx),
            "text": text,
            "url": f"{BASE_URL}/t/{slug}/{topic_id}/{post['post_number']}",
            "created_by": post["username"],
            "created_at": post["created_at"],
            "images_base64": images_b64
        })

    return thread_data

def main():
    page = 0
    output = []

    while True:
        url = f"{CATEGORY_URL}.json?page={page}"
        r = requests.get(url, headers=headers, cookies=cookies)
        if r.status_code != 200:
            break

        topics = r.json().get("topic_list", {}).get("topics", [])
        if not topics:
            break

        for topic in topics:
            created = datetime.strptime(topic["created_at"][:10], "%Y-%m-%d")
            if not (START_DATE <= created <= END_DATE):
                continue

            topic_id = topic["id"]
            slug = topic["slug"]
            print(f"Fetching thread: {slug}")
            thread = fetch_thread(topic_id, slug)
            if thread:
                output.append(thread)
                time.sleep(1)

        page += 1

    with open("tds_threads.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(output)} threads to tds_threads.json")

if __name__ == "__main__":
    main()
