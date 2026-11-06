# BIS SmartAssist: AI-Powered Standards and Certification Assistant

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.x-61DAFB.svg?logo=react)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.x-646CFF.svg?logo=vite)](https://vitejs.dev)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4.x-FF4F00.svg)](https://www.trychroma.com)
[![Ollama](https://img.shields.io/badge/Ollama-Llama_3.2:3b-black.svg?logo=ollama)](https://ollama.com)

**BIS SmartAssist** is an intelligent full-stack AI assistant designed to navigate Indian Standards (IS), Bureau of Indian Standards (BIS) regulations, Quality Control Orders (QCOs), and product certification processes.

It integrates a high-performance Retrieval-Augmented Generation (RAG) architecture with multi-modal document intelligence (PDF and image OCR via native Tesseract), providing verified citations from official Indian Standards gazettes.

---

## 🏛️ System Architecture

```
React Frontend (Vite)
  ├── Text Queries ──────────────────────► POST /api/chat ──────────► ChromaDB (7,808 Records)
  └── Text + Documents (PDF/PNG/JPG) ───► POST /api/chat-with-files ─┐
                                                                      │
     ┌────────────────────────────────────────────────────────────────┘
     ▼
FastAPI Backend
  ├── Document Processor (document_processor.py)
  │     ├── Magic Byte & File Header Validation (%PDF-, \x89PNG, \xff\xd8)
  │     ├── Chunk-Based Streaming File Reader (10 MB Max, Early Abort)
  │     ├── PyMuPDF Text Extraction & Page Tracking
  │     └── Native Tesseract OCR Engine (Scanned PDFs & Images)
  │
  └── RAG Service (rag_service.py)
        ├── In-Memory Semantic Ranking (all-MiniLM-L6-v2)
        ├── ChromaDB Vector Search (Read-Only Persistent Collection)
        ├── Strict Untrusted Context Segregation (<untrusted_user_submissions>)
        └── Ollama Local LLM Synthesis (llama3.2:3b)
              │
              ▼
React Thread Interface (Thread.jsx)
  ├── Structured Compliance Analysis
  ├── Document Processing Status Chips
  └── Dual Citation Badges ([User Doc] vs [BIS Standard])
```

---

## ✨ Key Capabilities

- **Authoritative BIS Standards Knowledge Base**: Indexed collection of 7,808 official BIS records, QCO gazette notifications, and testing guidelines.
- **Multimodal Document Understanding**: Upload PDF documents, testing reports, and product label photos (PNG, JPG, JPEG).
- **Native OCR Engine**: PyMuPDF page-by-page extraction combined with Tesseract OCR 5.4.0 for scanned PDFs and raster image labels.
- **Strict Vector Isolation**: Uploaded documents are processed in-memory using unit-normalized cosine similarity embeddings and are **never** written into the permanent ChromaDB collection, preventing database contamination.
- **Prompt Injection & Adversarial Hardening**: Segregated XML delimiters (`<untrusted_user_submissions>` vs `<official_bis_knowledge_base>`) protect the LLM from system override instructions in untrusted applicant files.
- **Streaming Ingestion Security**: Chunk-based file streaming with instantaneous HTTP 413 rejection for files exceeding 10 MB to prevent memory exhaustion attacks.
- **Dual Source Citations**: Every answer distinguishes between user-uploaded claims and legal BIS mandates.

---

## 📂 Project Organization

```
BIS-SmartAssist/
├── Backend/
│   ├── config.py             # Centralized Pydantic settings & environment manager
│   ├── document_processor.py # PyMuPDF text extractor & Tesseract OCR pipeline
│   ├── main.py               # FastAPI application with lifespan model warmup
│   ├── rag_service.py        # RAG pipeline, in-memory embeddings & Ollama driver
│   ├── requirements.txt      # Pinned Python dependencies
│   ├── .env.example          # Environment variables template
│   └── .env                  # Local environment file (git-ignored)
├── Frontend/
│   └── bis-smartassist-react/bis-smartassist/
│       ├── src/
│       │   ├── components/   # Composer, Thread, Sidebar, Topbar, Auth
│       │   ├── utils/        # bisApi.js, bisAnswers.js, logo.js
│       │   ├── App.jsx       # Multi-file staging & route dispatching
│       │   └── index.css     # Responsive glassmorphism styling
│       ├── .env.example      # Frontend environment template
│       └── package.json      # React dependencies & scripts
├── chroma_db/                # Pre-indexed ChromaDB vector database (7,808 records)
├── Data/                     # Source BIS standards, QCO gazettes, and guidelines
├── rag/                      # Offline ingestion scripts and data unification
├── .gitignore                # Exclusion rules for virtualenvs, caches & secrets
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python**: 3.10+ (tested on Python 3.14)
- **Node.js**: 18+ & npm
- **Ollama**: Installed and running locally
  ```bash
  ollama run llama3.2:3b
  ```
- **Tesseract OCR**: (Optional, for image and scanned PDF OCR)
  - Windows: UB-Mannheim Tesseract OCR 5.4.0+

### 2. Backend Setup
```bash
cd Backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend Setup
```bash
cd Frontend/bis-smartassist-react/bis-smartassist
npm install
cp .env.example .env
npm run dev
```

Visit `http://localhost:5173` to access the chat interface.

---

## 🛡️ Security & Reliability

- **File Header Magic Byte Validation**: Files are checked against cryptographic magic bytes (`%PDF-`, `\x89PNG`, `\xff\xd8`).
- **Path Traversal Protection**: Filenames are sanitized with regex character stripping (`sanitize_filename`).
- **Memory Safety**: Files are read in 1 MB chunks and aborted immediately if cumulative size exceeds 10 MB.
- **Fail-Safe Fallbacks**: Extractive rule-based responses are returned if the local Ollama LLM or ChromaDB is temporarily unreachable.

---

## 📜 License
Apache-2.0 License. All BIS standards referenced remain the intellectual property of the Bureau of Indian Standards, Government of India.

