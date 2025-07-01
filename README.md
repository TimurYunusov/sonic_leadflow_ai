# Sonic LeadFlowAI

## Project Overview
Sonic LeadFlowAI is an AI-driven lead generation pipeline that combines FastAPI, LangGraph, Playwright, and various enrichment and scraping tools. It features a robust backend for scraping, enrichment, and lead management, and a modern Next.js frontend for user interaction.

## Key Features & Progress
- **Async, robust scraping and enrichment pipeline** using Playwright, Firecrawl, and LLMs
- **Supabase** for structured business/lead data and workflow logs
- **Pinecone** for semantic search and RAG
- **LangGraph** orchestrates a multi-step pipeline:
  1. Scrape Google Maps for businesses
  2. Extract and enrich business info
  3. Check Supabase for existing leads
  4. For new/incomplete leads: extract domain, find email, summarize website, analyze pain points, generate outreach email
  5. Store all data in Supabase and embeddings in Pinecone
- **All pipeline nodes are async** and use `await` (no `asyncio.run()` in nodes/endpoints)
- **FastAPI** exposes `/run-leadflow-pipeline` endpoint for running the pipeline
- **Next.js frontend** (in `leadflow_ui/`) for user interface
- **Improved error handling, logging, and CORS support**
- **.gitignore** updated to exclude frontend build/dependency files

## Running the Project with Docker (Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your machine

### 1. Dockerfile for Backend (FastAPI)
Create `leadflow_ai/Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --upgrade pip && pip install -r requirements.txt
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Dockerfile for Frontend (Next.js)
Create `leadflow_ui/Dockerfile`:
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### 3. docker-compose.yml (in project root)
```yaml
version: "3.8"
services:
  backend:
    build: ./leadflow_ai
    ports:
      - "8000:8000"
    volumes:
      - ./leadflow_ai:/app
  frontend:
    build: ./leadflow_ui
    ports:
      - "3000:3000"
    volumes:
      - ./leadflow_ui:/app
    depends_on:
      - backend
```

### 4. Start the Project
From the project root, run:
```sh
docker-compose up --build
```
- FastAPI backend: [http://localhost:8000](http://localhost:8000)
- Next.js frontend: [http://localhost:3000](http://localhost:3000)

---

## Manual Setup (Alternative)

### Backend (FastAPI)
```sh
cd sonic_leadflow_ai/leadflow_ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

### Frontend (Next.js)
```sh
cd leadflow_ui
npm install
npm run dev
```

---

## Notes
- Ensure CORS is enabled in FastAPI for frontend-backend communication.
- All sensitive and build files are excluded via `.gitignore`.
- For production, configure environment variables and secrets securely.

---

**Happy hacking with Sonic LeadFlowAI!**