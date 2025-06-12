# 📘 TDS TA Repository

This repository contains all the scripts and configurations needed to scrape data, generate embeddings, store vectors in Qdrant, and deploy an API for the **TDS (Tools in Data Science)** course.

---

## 🧾 Step 1: Scrape Course Content from GitHub

- Run `course_scrape.py` to scrape course content hosted by **Mr. S Anand** on GitHub.

---

## 🗓 Step 2: Scrape TDS Discourse Posts (from 1 Jan 2025 to 14 Apr 2025)

- Run `discourse_scrape.py` to scrape posts from the TDS Discourse forum.
- Replace the cookie values (`_t` and `_forum_session`) in the script:
  1. Open the browser DevTools (Inspect → Network tab).
  2. Look for any fetch request.
  3. Copy your `_t` and `_forum_session` cookies and paste them in the script.

---

## 🧠 Step 3: Generate Embeddings

- Set your `AIPIPE_TOKEN` in the script.
- Run `embedding.py` to create embeddings from the scraped content.
- The embeddings will be saved in a `.json` file.

---

## ☁️ Step 4: Upload to Qdrant Cloud

- Create a **cluster** in [Qdrant Cloud](https://qdrant.tech/).
- Replace the following in your script:
  - `QDRANT_URL` with your Qdrant cluster URL.
  - `QDRANT_API_KEY` with your Qdrant API key.
  - `COLLECTION_NAME` with your desired collection name.
- Run `upload_qdrant`.py to upload the embedding in Qdrant.

---

## 🚀 Step 5: Deploy API Endpoint

- cd api
- Ensure the following keys are added to your `.env` file:
  - `OPENAI_API_KEY` or your **AIPipe key**
  - `QDRANT_API_KEY` from Qdrant
  - `QDRANT_URL` (your Qdrant cluster URL)
- Run the deployment script (e.g., `main.py` or `api.py` depending on your implementation).

## ✅ Step 6: Test Responses Using Promptfoo

### 📂 Setup

- Make sure `promptfoo` is installed globally or in your environment:

  ```bash
  npm install -g promptfoo

  ```

- Run promptfoo eval -c promptfoo.yaml --clear-cache
