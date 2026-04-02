# 🏥 MediBot — AI-Powered Medical Chatbot

> A production-ready conversational AI for medical information, built with Python, Flask, LangChain, Pinecone, and OpenAI.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask)
![LangChain](https://img.shields.io/badge/LangChain-0.2-1C3C3C?style=flat)
![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-00B388?style=flat)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-412991?style=flat&logo=openai)
![Vercel](https://img.shields.io/badge/Frontend-Vercel-black?style=flat&logo=vercel)
![Render](https://img.shields.io/badge/Backend-Render-46E3B7?style=flat)

---

## 📋 Overview

MediBot is a **Retrieval-Augmented Generation (RAG)** medical chatbot that answers health questions by searching a curated medical knowledge base. It combines:

- **LangChain** for orchestrating the AI pipeline
- **Pinecone** as the vector database for semantic document search
- **OpenAI GPT** as the language model for generating answers
- **Flask** as the REST API backend
- **Vanilla HTML/CSS/JS** for the responsive chat frontend

### Key Features

| Feature | Details |
|---------|---------|
| 🔍 RAG Pipeline | Retrieves relevant medical docs before generating answers |
| 🧠 Memory | Maintains multi-turn conversation history per session |
| 🚨 Safety | Detects emergencies, blocks diagnosis requests, adds disclaimers |
| 📄 PDF Support | Load your own medical PDFs into the knowledge base |
| 🔐 Secure | Input sanitization, CORS protection, env variable management |
| 🚀 Deployed | Backend on Render, Frontend on Vercel |

---

## 🏗️ Project Architecture

```
┌─────────────────────────────────────────────────────┐
│                   USER BROWSER                       │
│              (Frontend — Vercel)                     │
│          HTML + CSS + JavaScript                     │
└─────────────────────┬───────────────────────────────┘
                      │ POST /api/chat
                      ▼
┌─────────────────────────────────────────────────────┐
│               FLASK REST API                         │
│              (Backend — Render)                      │
│                                                      │
│  ┌─────────────┐    ┌──────────────────────────┐    │
│  │  Safety     │    │   LangChain RAG Chain     │    │
│  │  Module     │    │                          │    │
│  │  - Emergency│    │  ConversationalRetrieval  │    │
│  │  - Diagnosis│    │  Chain + Memory           │    │
│  │  - Sanitize │    └──────────┬───────────────┘    │
│  └─────────────┘               │                    │
└───────────────────────────────┼────────────────────┘
                                │
              ┌─────────────────┴─────────────────────┐
              │                                        │
              ▼                                        ▼
┌─────────────────────┐              ┌────────────────────────┐
│   PINECONE          │              │   OPENAI API           │
│   Vector Store      │              │                        │
│                     │◄────────────►│  text-embedding-ada    │
│  - Medical chunks   │  embeddings  │  (for vector search)   │
│  - Semantic search  │              │                        │
│  - Top-k retrieval  │              │  gpt-3.5-turbo         │
└─────────────────────┘              │  (for generation)      │
                                     └────────────────────────┘
```

---

## 📁 Folder Structure

```
medical-chatbot/
│
├── backend/
│   ├── app.py                    # Flask app entry point
│   ├── ingest.py                 # Run once to load docs into Pinecone
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment variable template
│   ├── data/                     # Put your medical PDFs here
│   │   └── sample_medical_data.txt
│   └── src/
│       ├── chains/
│       │   └── rag_chain.py      # LangChain RAG + memory logic
│       ├── routes/
│       │   └── chat_routes.py    # Flask API endpoints
│       └── utils/
│           ├── vector_store.py   # Pinecone operations
│           └── safety.py         # Emergency detection, disclaimers
│
├── frontend/
│   ├── index.html                # Chat UI
│   ├── vercel.json               # Vercel deployment config
│   └── static/
│       ├── css/
│       │   └── style.css         # UI styles
│       └── js/
│           └── app.js            # Frontend JavaScript
│
├── render.yaml                   # Render deployment config
├── .gitignore
└── README.md
```

---

## ⚙️ Prerequisites

- Python 3.10+
- OpenAI API key — [Get one here](https://platform.openai.com/api-keys)
- Pinecone account — [Sign up free](https://app.pinecone.io)
- Git

---

## 🚀 Quick Start (Local Development)

### Step 1 — Clone the repository

```bash
git clone https://github.com/yourusername/medical-chatbot.git
cd medical-chatbot
```

### Step 2 — Set up the backend

```bash
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate     # Mac/Linux
# OR
venv\Scripts\activate        # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 3 — Configure environment variables

```bash
# Copy the template
cp .env.example .env

# Open .env and fill in your keys:
# OPENAI_API_KEY=sk-...
# PINECONE_API_KEY=...
# PINECONE_INDEX_NAME=medical-chatbot
```

### Step 4 — Add medical documents (optional but recommended)

```bash
# Add your PDF files to the data folder
cp your-medical-textbook.pdf data/

# The sample_medical_data.txt is already there for testing
```

### Step 5 — Ingest documents into Pinecone

```bash
# Run this ONCE to populate your vector database
python ingest.py

# Output:
# 📄 Loaded 1 document pages.
# ✂️  Split into 47 chunks.
# ⬆️  Uploading embeddings to Pinecone...
# ✅ Documents successfully ingested into Pinecone!
```

### Step 6 — Start the Flask API

```bash
python app.py

# Output:
# 🏥 Medical Chatbot API starting on port 5000...
# * Running on http://0.0.0.0:5000
```

### Step 7 — Open the frontend

```bash
# Option A: Open directly in browser
open ../frontend/index.html

# Option B: Serve with Python (recommended to avoid CORS issues)
cd ../frontend
python -m http.server 3000
# Then visit http://localhost:3000
```

---

## 🧪 Test the API

```bash
# Test the health endpoint
curl http://localhost:5000/health

# Test the chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the symptoms of diabetes?", "session_id": "test123"}'

# Expected response:
# {
#   "answer": "Diabetes symptoms include...\n\n---\n⚕️ Medical Disclaimer...",
#   "sources": ["backend/data/sample_medical_data.txt"],
#   "session_id": "test123",
#   "safety_triggered": false
# }
```

---

## 🌐 Deployment

### Backend → Render

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Set **Root Directory**: `backend`
5. Set **Build Command**: `pip install -r requirements.txt`
6. Set **Start Command**: `gunicorn "app:create_app()" --workers 2 --bind 0.0.0.0:$PORT`
7. Add **Environment Variables** in Render dashboard:
   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY`
   - `PINECONE_INDEX_NAME`
   - `FLASK_ENV` = `production`
8. Deploy! Copy the URL (e.g., `https://medibot-api.onrender.com`)

### Frontend → Vercel

1. Update `API_BASE_URL` in `frontend/static/js/app.js` with your Render URL
2. Go to [vercel.com](https://vercel.com) → New Project
3. Import your GitHub repo
4. Set **Root Directory**: `frontend`
5. Deploy!

---

## 🛡️ Safety Features

| Scenario | Behavior |
|----------|---------|
| Emergency keywords detected | Returns emergency hotlines immediately, no LLM call |
| Diagnosis request | Redirects to professional consultation |
| Prompt injection attempt | Input is sanitized |
| All AI responses | Medical disclaimer appended automatically |
| Input length | Capped at 1000 characters |

---

## 🔧 Customization

### Swap to a different LLM

In `.env`, change:
```
OPENAI_MODEL=gpt-4              # More accurate, more expensive
OPENAI_MODEL=gpt-3.5-turbo      # Default (cost-effective)
```

### Add more medical documents

```bash
# Add PDFs to backend/data/ and re-run:
python ingest.py
```

### Adjust RAG parameters

In `src/chains/rag_chain.py`:
- `k=4` → number of document chunks retrieved per query
- `temperature=0.3` → lower = more factual

---

## 📚 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend Framework | Flask 3.0 | REST API |
| AI Orchestration | LangChain | RAG pipeline, memory |
| Language Model | OpenAI GPT-3.5/4 | Text generation |
| Embeddings | OpenAI Ada-002 | Vector representation |
| Vector Database | Pinecone | Semantic search |
| PDF Loading | LangChain PyPDFLoader | Document ingestion |
| Memory | ConversationBufferWindowMemory | Chat history |
| Frontend | HTML/CSS/JavaScript | Chat UI |
| Backend Deploy | Render | Python hosting |
| Frontend Deploy | Vercel | Static hosting |

---

## 📄 License

MIT License — feel free to use this for learning and projects.

---

## ⚕️ Medical Disclaimer

This chatbot is for **educational and informational purposes only**. It does not provide medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional for medical decisions.

---

*Built with ❤️ using LangChain, Pinecone, OpenAI, and Flask*
