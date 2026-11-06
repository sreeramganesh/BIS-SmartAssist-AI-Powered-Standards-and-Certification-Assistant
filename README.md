# BIS SmartAssist
### AI-Powered Standards and Certification Assistant

<p align="center">
  <strong>Making Indian Standards and BIS Certification More Accessible Through Artificial Intelligence</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-18.x-61DAFB?logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/Vite-5.x-646CFF?logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/FastAPI-0.110.0-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/ChromaDB-Vector%20Database-FF4F00" alt="ChromaDB">
  <img src="https://img.shields.io/badge/Ollama-Llama%203.2%3A3b-black?logo=ollama" alt="Ollama">
  <img src="https://img.shields.io/badge/Architecture-RAG-blueviolet" alt="RAG">
  <img src="https://img.shields.io/badge/License-Apache%202.0-green" alt="License">
</p>

---

## 📌 Project Overview

**BIS SmartAssist** is an AI-powered intelligent assistant developed to simplify access to Indian Standards, Bureau of Indian Standards (BIS) regulations, Quality Control Orders (QCOs), product certification procedures, and related technical documentation.

Understanding Indian Standards and BIS certification requirements can be challenging because relevant information is distributed across technical documents, regulations, government notifications, testing guidelines, and certification procedures.

BIS SmartAssist addresses this challenge through a **Retrieval-Augmented Generation (RAG)** architecture that combines semantic document retrieval with a locally running Large Language Model (LLM).

Users can ask questions in natural language, receive context-aware responses, explore relevant BIS information, and upload supporting documents for document-based analysis.

The system retrieves relevant information from its indexed BIS knowledge base and uses the retrieved context to generate responses with supporting source references.

### 🎯 Project Objectives

- Simplify access to Indian Standards and BIS-related information.
- Reduce the effort required to search through lengthy technical documents.
- Provide context-aware answers using Retrieval-Augmented Generation.
- Assist users in understanding certification procedures and requirements.
- Support document-based question answering through PDF and image uploads.
- Improve accessibility to technical and regulatory information through a conversational interface.
- Maintain separation between the permanent BIS knowledge base and temporary user-uploaded documents.

---

## ✨ Key Features

### 1. AI-Powered Conversational Assistant

Interact with BIS SmartAssist using natural language.

Users can ask questions related to:

- Indian Standards (IS).
- BIS certification procedures.
- Quality Control Orders (QCOs).
- Product testing requirements.
- Certification documentation.
- Product-related regulatory information.
- BIS guidelines and technical requirements.

The assistant retrieves relevant information and generates responses using the local LLM.

### 2. Retrieval-Augmented Generation (RAG)

BIS SmartAssist uses RAG to improve the relevance and contextual grounding of AI-generated responses.

Instead of depending entirely on the LLM's pretrained knowledge, the system retrieves relevant information from the BIS document collection before generating an answer.

Key components:

- Semantic search using Sentence Transformers.
- Vector similarity retrieval through ChromaDB.
- Context preparation and document ranking.
- Context-aware answer generation using Ollama.
- Source references to support generated responses.

### 3. BIS Knowledge Base

The application uses a pre-indexed ChromaDB collection containing **7,808 records**.

The knowledge base includes indexed BIS-related materials such as:

- Indian Standards documentation.
- BIS certification information.
- Quality Control Orders.
- Government notifications.
- Product testing guidelines.
- Technical and regulatory documents.

The vector database enables semantic retrieval of relevant information based on the user's question.

### 4. Document-Based Question Answering

Users can upload documents and ask questions about their contents.

Supported file formats:

| File Format | Extension |
|---|---|
| PDF | `.pdf` |
| PNG Image | `.png` |
| JPEG Image | `.jpg`, `.jpeg` |

Example use cases:

- Understanding product testing reports.
- Extracting information from technical documents.
- Reviewing product labels.
- Asking questions about uploaded certification documents.
- Comparing uploaded information with retrieved BIS knowledge.

PDF text extraction is handled using PyMuPDF. Scanned documents and images require a correctly installed and configured Tesseract OCR engine.

### 5. Separate User Documents and BIS Knowledge

The system maintains a separation between uploaded documents and the permanent BIS knowledge base.

- Official BIS records are retrieved from the existing ChromaDB collection.
- Uploaded documents are processed separately.
- Uploaded document embeddings are generated in memory.
- User-uploaded content is not permanently inserted into the official BIS vector collection.
- Retrieved information can be presented with separate source labels.

This approach helps preserve the integrity of the existing BIS knowledge base.

### 6. Dual Source References

Responses can distinguish between two information sources:

**BIS Standard**
- Information retrieved from the indexed BIS knowledge base.
- Used to provide relevant standards and regulatory context.

**User Document**
- Information extracted from documents uploaded by the user.
- Used to answer questions about the submitted material.

This separation helps users understand whether a statement comes from the uploaded document or the indexed BIS knowledge base.

### 7. Modern Interactive Interface

The application provides a conversational interface built with React.

Interface capabilities include:

- Chat-based question and answer experience.
- Conversation thread interface.
- Sidebar navigation.
- File attachment and multi-file staging.
- Document upload status.
- Source reference indicators.
- Structured AI responses.
- Responsive application layout.

---

## 🏗️ System Architecture

BIS SmartAssist follows a modular full-stack architecture.

```text
                  USER
                   |
                   v
        +-----------------------+
        |    React Frontend     |
        |       Vite            |
        +-----------------------+
                   |
                   v
        +-----------------------+
        |    FastAPI Backend    |
        |                       |
        |  /api/chat            |
        |  /api/chat-with-files |
        +-----------------------+
                   |
          +--------+--------+
          |                 |
          v                 v
 +----------------+  +----------------------+
 | Document       |  | RAG Service          |
 | Processor      |  |                      |
 |                |  | Sentence Transformers|
 | PyMuPDF        |  | ChromaDB              |
 | Tesseract OCR  |  | Context Retrieval     |
 +----------------+  +----------------------+
          |                 |
          |                 v
          |        +----------------------+
          |        | BIS Knowledge Base   |
          |        |                      |
          |        | 7,808 Records        |
          |        | ChromaDB             |
          |        +----------------------+
          |                 |
          +--------+--------+
                   |
                   v
        +-----------------------+
        |     Ollama LLM        |
        |     Llama 3.2:3b      |
        +-----------------------+
                   |
                   v
        +-----------------------+
        | Generated Response    |
        |                       |
        | Answer + Sources      |
        +-----------------------+
                   |
                   v
        +-----------------------+
        |    React Interface    |
        +-----------------------+
```

### Architecture Components

| Component | Technology | Responsibility |
|---|---|---|
| Frontend | React | User interface and interaction |
| Build Tool | Vite | Frontend development and build |
| Backend | FastAPI | API handling and application logic |
| Embedding Model | all-MiniLM-L6-v2 | Semantic text embeddings |
| Vector Database | ChromaDB | BIS knowledge storage and retrieval |
| LLM Runtime | Ollama | Local language model execution |
| Language Model | Llama 3.2:3b | Context-aware response generation |
| PDF Processing | PyMuPDF | PDF text extraction |
| OCR | Tesseract | Text extraction from scanned documents and images |

---

## 🔄 How It Works

BIS SmartAssist processes user questions through the following workflow.

### Step 1: User Query

The user enters a question through the React-based chat interface.

Example:

> What are the BIS certification requirements for aluminium utensils?

### Step 2: API Request

The frontend sends the user's question to the FastAPI backend.

For normal questions:

```http
POST /api/chat
```

For questions involving uploaded documents:

```http
POST /api/chat-with-files
```

### Step 3: Semantic Embedding

The Sentence Transformer model converts the user's question into a numerical vector representation.

**Embedding Model:**

`all-MiniLM-L6-v2`

These embeddings allow the system to identify documents with semantically relevant content.

### Step 4: Knowledge Retrieval

ChromaDB performs vector similarity search against the existing BIS knowledge collection.

The system retrieves relevant document chunks that can help answer the question.

### Step 5: Context Preparation

The retrieved BIS information and, when applicable, extracted user-document content are prepared as separate context sources.

This allows the system to distinguish official knowledge-base material from user-provided content.

### Step 6: LLM Response Generation

The retrieved context is passed to the locally running LLM through Ollama.

**LLM:**

`llama3.2:3b`

The model uses the supplied context to generate a natural-language response.

### Step 7: Response Display

The backend returns the generated answer and available source information to the React frontend.

The response is displayed in the conversation interface.

---

## 🧠 Retrieval-Augmented Generation (RAG)

RAG is the core intelligence mechanism behind BIS SmartAssist.

It combines information retrieval with language generation.

### Why RAG?

A conventional LLM may generate answers using information learned during training. However, this does not guarantee that its responses accurately reflect specific BIS documents or regulatory requirements.

RAG addresses this limitation by retrieving relevant information from an external knowledge base before generating the answer.

### RAG Workflow

```text
User Question
      |
      v
Text Embedding
      |
      v
Vector Similarity Search
      |
      v
ChromaDB Retrieval
      |
      v
Relevant Document Chunks
      |
      v
Context Preparation
      |
      v
Ollama LLM
      |
      v
Context-Aware Answer
      |
      v
Source References
```

### RAG Technologies

| Technology | Purpose |
|---|---|
| Sentence Transformers | Converts text into embeddings |
| all-MiniLM-L6-v2 | Embedding model |
| ChromaDB | Stores and retrieves document vectors |
| Ollama | Runs the local LLM |
| Llama 3.2:3b | Generates responses using retrieved context |

---

## 📂 Project Structure

```text
BIS-SmartAssist/
│
├── Backend/
│   │
│   ├── config.py
│   ├── main.py
│   ├── rag_service.py
│   ├── document_processor.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
├── Frontend/
│   │
│   └── bis-smartassist-react/
│       │
│       └── bis-smartassist/
│           ├── public/
│           ├── src/
│           │   ├── components/
│           │   │   ├── AuthScreen.jsx
│           │   │   ├── BrandLogo.jsx
│           │   │   ├── Composer.jsx
│           │   │   ├── EmptyState.jsx
│           │   │   ├── Sidebar.jsx
│           │   │   ├── Thread.jsx
│           │   │   └── Topbar.jsx
│           │   │
│           │   ├── utils/
│           │   │   ├── bisApi.js
│           │   │   └── bisAnswers.js
│           │   │
│           │   ├── App.jsx
│           │   ├── main.jsx
│           │   └── index.css
│           │
│           ├── .env.example
│           └── package.json
│
├── chroma_db/
│
├── Data/
│
├── rag/
│
├── .gitignore
│
└── README.md
```

### Important Directories

**Backend/**
- Contains the FastAPI application.
- Implements the RAG service.
- Handles uploaded document processing.
- Manages application configuration.

**Frontend/**
- Contains the React application.
- Implements the chat interface.
- Handles API communication and file uploads.

**chroma_db/**
- Contains the pre-indexed ChromaDB knowledge collection.
- Stores vector representations and associated metadata.

**Data/**
- Contains source BIS-related documents used in the knowledge-base preparation process.

**rag/**
- Contains scripts related to document ingestion and knowledge-base preparation.

---

## 🛠️ Technology Stack

### Frontend

| Technology | Description |
|---|---|
| React | Component-based user interface |
| Vite | Frontend development and build tool |
| JavaScript | Application logic |
| CSS | Interface styling |

### Backend

| Technology | Description |
|---|---|
| Python | Core backend programming language |
| FastAPI | REST API framework |
| Pydantic Settings | Environment configuration |
| Uvicorn | ASGI application server |

### Artificial Intelligence

| Technology | Description |
|---|---|
| Sentence Transformers | Semantic embedding generation |
| all-MiniLM-L6-v2 | Text embedding model |
| Ollama | Local LLM execution |
| Llama 3.2:3b | Language generation |

### Database and Document Processing

| Technology | Description |
|---|---|
| ChromaDB | Vector database |
| PyMuPDF | PDF text extraction |
| Tesseract OCR | Optical character recognition |
| Pillow | Image processing |

---

## ⚙️ Installation and Setup

Follow these steps to run BIS SmartAssist locally.

### 1. Prerequisites

Install the following software:

- Python 3.10 or later
- Node.js 18 or later
- npm
- Git
- Ollama
- Tesseract OCR (for scanned PDF and image text extraction)

### 2. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/BIS-SmartAssist.git

cd BIS-SmartAssist
```

Replace `YOUR_USERNAME` with your GitHub username.

### 3. Set Up Ollama

Install Ollama and download the required model.

```bash
ollama pull llama3.2:3b
```

Verify the model:

```bash
ollama list
```

Run the model:

```bash
ollama run llama3.2:3b
```

Keep Ollama running while using the application.

### 4. Configure Tesseract OCR

Tesseract is required for OCR-based extraction from scanned PDFs and images.

On Windows, install Tesseract OCR using a compatible Windows installer.

Verify installation:

```bash
tesseract --version
```

Ensure the Tesseract executable is available through the system PATH.

If Tesseract is not configured, scanned-document and image OCR functionality may be unavailable.

### 5. Backend Setup

Navigate to the backend directory:

```bash
cd Backend
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the environment.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```cmd
.venv\Scripts\activate.bat
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create your environment configuration:

**Windows:**

```powershell
Copy-Item .env.example .env
```

**Linux/macOS:**

```bash
cp .env.example .env
```

Configure the required values in `.env` based on your local setup.

Start the FastAPI backend:

```bash
python -m uvicorn main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Frontend Setup

Open a new terminal.

Navigate to the frontend directory:

```bash
cd Frontend/bis-smartassist-react/bis-smartassist
```

Install dependencies:

```bash
npm install
```

Create the frontend environment file:

**Windows:**

```powershell
Copy-Item .env.example .env
```

**Linux/macOS:**

```bash
cp .env.example .env
```

Configure the backend API URL in the frontend environment file.

Example:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Start the development server:

```bash
npm run dev
```

Open the application:

```text
http://localhost:5173
```

---

## 🔌 Backend API Endpoints

The application exposes FastAPI endpoints for interacting with the assistant.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/chat` | Processes normal text-based questions |
| POST | `/api/chat-with-files` | Processes questions with uploaded documents |

### 1. Text-Based Chat

```http
POST /api/chat
```

Used for standard conversational questions.

Example question:

<img width="1902" height="912" alt="home page " src="https://github.com/user-attachments/assets/b0ba7d59-8d61-4f54-b71d-1dfb40229540" />


### 2. Document-Based Chat

<img width="1917" height="911" alt="response page " src="https://github.com/user-attachments/assets/c2063e4e-f5cc-48c2-a7ac-73fe68441195" /> 


Used when users want to submit documents along with their questions.

Supported formats:

- PDF
- PNG
- JPG
- JPEG

The backend processes the uploaded documents and uses the extracted content during response generation.

For the exact request fields and response schema, refer to the FastAPI Swagger documentation.

---

## 🔐 Security and Data Handling

BIS SmartAssist incorporates several document-handling and data-isolation considerations.

### File Validation

Uploaded documents are checked for supported file types and expected file signatures.

### Document Isolation

User-uploaded documents are processed separately from the permanent BIS knowledge base.

### Temporary Processing

Uploaded document embeddings are generated in memory rather than being permanently inserted into the existing ChromaDB collection.

### Context Separation

Official BIS knowledge and user-provided document content are treated as separate information sources during response generation.

### Local Language Model

Ollama runs the configured language model locally, allowing the application to use local inference rather than depending on a hosted LLM API.

**Important:** BIS SmartAssist is an informational assistant. Its responses should not be treated as official BIS certification decisions, legal advice, or a substitute for verifying applicable standards and government notifications.

---

## 📊 Knowledge Base Information

| Property | Configuration |
|---|---|
| Vector Database | ChromaDB |
| Collection | `bis_smartassist` |
| Indexed Records | 7,808 |
| Embedding Model | `all-MiniLM-L6-v2` |
| Language Model | `llama3.2:3b` |
| LLM Runtime | Ollama |
| Retrieval Approach | Semantic Vector Search |

**Note:** The existing ChromaDB collection contains pre-indexed BIS records. Do not recreate or overwrite this collection during normal application startup.

---

## 🧪 Testing and Validation

The application can be validated using the following test scenarios.

| Test Scenario | Expected Behavior |
|---|---|
| Normal BIS-related question | Generates a context-aware response |
| Certification-related question | Retrieves relevant BIS information |
| Unrelated question | Avoids unsupported BIS claims |
| PDF upload | Extracts available document text |
| Scanned PDF upload | Uses OCR when Tesseract is configured |
| Image upload | Uses OCR when Tesseract is configured |
| Multiple document uploads | Processes supported uploaded files |
| Unsupported file upload | Rejects unsupported formats |
| Corrupted PDF upload | Handles document-processing errors |
| Ollama unavailable | Handles LLM connection failure |
| ChromaDB unavailable | Handles retrieval failure |

---

## 🚀 Future Enhancements

Potential improvements for future versions include:

- User authentication and role-based access control.
- Persistent conversation history.
- PostgreSQL or Supabase integration.
- Advanced hybrid search using keyword and semantic retrieval.
- Improved document reranking.
- More comprehensive BIS standards coverage.
- Multilingual question answering.
- Advanced certification workflow assistance.
- Improved document comparison and compliance analysis.
- Performance optimization for local LLM inference.
- Expanded automated testing and evaluation.

---

## 📸 Application Screenshots

Add screenshots of the actual application here.

Suggested screenshots:

1. Application landing page.
2. Main conversational assistant.
3. BIS-related question and answer.
4. Document upload interface.
5. Document-based question answering.
6. Response with source references.

Example:

```markdown
![BIS SmartAssist Dashboard](screenshots/dashboard.png)

![Document Upload Interface](screenshots/document-upload.png)

![AI Response Interface](screenshots/ai-response.png)
```

---

## 👨‍💻 Development

BIS SmartAssist is developed using a modular architecture that separates frontend presentation, backend API handling, document processing, knowledge retrieval, and language generation.

The project is intended to demonstrate how Retrieval-Augmented Generation and locally running language models can make technical and regulatory information easier to access.

---

## 📜 License

This project is licensed under the **Apache License 2.0**.

See the `LICENSE` file for more information.

Indian Standards and other BIS-related source materials remain subject to their respective ownership, copyright, licensing, and usage conditions. This project is not affiliated with or officially endorsed by the Bureau of Indian Standards unless explicitly stated.

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

Your feedback and contributions are welcome.

---

<p align="center">
  <strong>BIS SmartAssist</strong><br>
  AI-Powered Access to Indian Standards and Certification Information
</p>
