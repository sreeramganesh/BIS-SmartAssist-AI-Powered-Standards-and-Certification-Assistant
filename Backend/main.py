from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings
from rag_service import init_rag_service, ask_bis, ask_bis_with_documents


# ============================================================
# FASTAPI LIFESPAN (ASYNC INITIALIZATION)
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager. Loads SentenceTransformer
    and initializes ChromaDB connection cleanly on server startup.
    Ensures models are loaded only once in memory.
    """
    print("[STARTUP] Initializing BIS SmartAssist services...", flush=True)
    try:
        init_rag_service()
        print("[STARTUP] All BIS SmartAssist services initialized and ready.", flush=True)
    except Exception as error:
        print(f"[STARTUP ERROR] Model/database warmup failed: {error}", flush=True)
    yield
    print("[SHUTDOWN] BIS SmartAssist backend shutting down.", flush=True)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="BIS SmartAssist API",
    version="2.0.0",
    description="AI-Powered Intelligent Assistant for Indian Standards and BIS Services with Document Intelligence",
    lifespan=lifespan
)


# ============================================================
# CORS MIDDLEWARE
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST & RESPONSE MODELS
# ============================================================

class ChatRequest(BaseModel):
    question: str


# ============================================================
# ROOT & HEALTH CHECK ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {
        "message": "BIS SmartAssist Backend is running",
        "version": "2.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "BIS SmartAssist",
        "vector_db": "ChromaDB",
        "llm_model": settings.ollama_model
    }


# ============================================================
# CHAT ENDPOINTS
# ============================================================

@app.post("/api/chat")
def chat(request: ChatRequest):
    """
    Standard text-only RAG chat endpoint.
    Preserves exact contract for existing chatbot.
    """
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The 'question' field cannot be empty."
        )

    result = ask_bis(request.question)
    return result


@app.post("/api/chat-with-files")
async def chat_with_files(
    question: Optional[str] = Form(None),
    files: List[UploadFile] = File(...)
):
    """
    Multimodal RAG chat endpoint.
    Accepts user question and uploaded PDF documents or images (PNG, JPG, JPEG).
    Processes documents in isolated memory and retrieves relevant official BIS standards.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file must be uploaded."
        )

    if len(files) > settings.max_files_count:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many files uploaded ({len(files)}). Maximum allowed is {settings.max_files_count} files per request."
        )

    # Read uploaded file contents using chunked streaming to prevent memory exhaustion
    CHUNK_SIZE = 1024 * 1024  # 1 MB chunk buffer
    files_data = []

    for upload in files:
        try:
            content = bytearray()
            while True:
                chunk = await upload.read(CHUNK_SIZE)
                if not chunk:
                    break
                content.extend(chunk)
                if len(content) > settings.max_file_size_bytes:
                    size_mb = len(content) / (1024 * 1024)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File '{upload.filename}' exceeds maximum allowed size of {settings.max_file_size_mb} MB."
                    )

            files_data.append((upload.filename or "uploaded_file", bytes(content)))
        except HTTPException:
            raise
        except Exception as read_err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read uploaded file '{upload.filename}': {read_err}"
            )
        finally:
            await upload.close()

    try:
        user_question = (question or "").strip()
        result = ask_bis_with_documents(user_question, files_data)
        return result
    except Exception as process_err:
        print(f"[ERROR] chat_with_files failed: {process_err}", flush=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing documents and generating answer: {str(process_err)}"
        )
