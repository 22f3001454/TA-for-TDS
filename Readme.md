# 📘 TDS TA Repository

This repository contains all the scripts and configurations needed to scrape data, generate embeddings, store vectors in Qdrant, and deploy an API for the **TDS (Tools in Data Science)** course.

---

## ⚙️ Environment Setup

Before running any scripts, create a `.env` file in the root directory with the following variables:

```env
# OpenAI/AIPipe Configuration
OPENAI_API_KEY=your-openai-or-aipipe-api-key-here
OPENAI_BASE_URL=https://aipipe.org/openai/v1

# AIPipe Token (for embedding generation script)
AIPIPE_TOKEN=your-aipipe-token-here

# Qdrant Configuration
QDRANT_URL=your-qdrant-cluster-url-here
QDRANT_API_KEY=your-qdrant-api-key-here
QDRANT_COLLECTION=tds_kb
```

**Note:** All scripts now use environment variables instead of hardcoded values for better security and flexibility.

---

## 🧾 Step 1: Scrape Course Content from GitHub

- Run `course_scrape.py` to scrape course content hosted by **Mr. S Anand** on GitHub.
- Run `creating_json.py` to store in json format.
---

## 🗓 Step 2: Scrape TDS Discourse Posts (from 1 Jan 2025 to 14 Apr 2025)

- Run `discourse_scrape.py` to scrape posts from the TDS Discourse forum.
- Replace the cookie values (`_t` and `_forum_session`) in the script:
  1. Open the browser DevTools (Inspect → Network tab).
  2. Look for any fetch request.
  3. Copy your `_t` and `_forum_session` cookies and paste them in the script.

---

## 🧠 Step 3: Generate Embeddings

- Ensure your `.env` file has `AIPIPE_TOKEN` set (see Environment Setup section above).
- Run `embedding.py` to create embeddings from the scraped content.
- The embeddings will be saved in `vectors.json`.

---

## ☁️ Step 4: Upload to Qdrant Cloud

- Create a **cluster** in [Qdrant Cloud](https://qdrant.tech/).
  -  Create a **cluster** with size 1536 and distance Cosine.   
- Add the following to your `.env` file:
  - `QDRANT_URL` - your Qdrant cluster URL
  - `QDRANT_API_KEY` - your Qdrant API key
  - `QDRANT_COLLECTION` - your desired collection name (optional, defaults to "tds_kb")
- Run `upload_qdrant.py` to upload the embeddings to Qdrant.

---

## 🚀 Step 5: Deploy API Endpoint

- Ensure the following keys are added to your `.env` file in the root directory:
  - `OPENAI_API_KEY` - your **AIPipe key** or OpenAI API key
  - `OPENAI_BASE_URL` - base URL for OpenAI API (defaults to "https://aipipe.org/openai/v1" if not set)
  - `QDRANT_API_KEY` - from Qdrant
  - `QDRANT_URL` - your Qdrant cluster URL
- To run locally:
  ```bash
  cd api
  uvicorn main:app --reload
  ```
- The API will be available at `http://localhost:8000/api`

## ✅ Step 6: Test Responses Using Promptfoo

### 📂 Setup

- Make sure `promptfoo` is installed globally or in your environment:

  ```bash
  npm install -g promptfoo

  ```

- Run
  ```bash
  promptfoo eval -c promptfoo.yaml --clear-cache

  ```
## ✅ Step 7 : **Deploy to Vercel**:  
Structure your project with `vercel.json`, `requirements.txt`, and an `api/` folder containing `main.py`. Push to GitHub, import the repo into [vercel.com](https://vercel.com), and in **Project Settings → Environment Variables**, add the following:
  - `OPENAI_API_KEY`
  - `OPENAI_BASE_URL` (optional, defaults to "https://aipipe.org/openai/v1")
  - `QDRANT_API_KEY`
  - `QDRANT_URL`
  - `QDRANT_COLLECTION` (optional, defaults to "tds_kb")

Vercel will auto-deploy your FastAPI app at `https://<project-name>.vercel.app/api/`.
