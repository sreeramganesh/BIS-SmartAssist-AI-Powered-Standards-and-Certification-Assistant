import os
import re
import io
import shutil
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

import pymupdf
from PIL import Image
import pytesseract

from config import settings


# ============================================================
# CONFIGURE TESSERACT OCR PATH (IF INSTALLED)
# ============================================================

def find_tesseract_binary() -> Optional[str]:
    """
    Attempts to locate tesseract.exe from settings or standard installation paths.
    """
    if settings.tesseract_cmd and os.path.exists(settings.tesseract_cmd):
        return settings.tesseract_cmd

    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        shutil.which("tesseract")
    ]

    for p in common_paths:
        if p and os.path.exists(p):
            return p

    return None


TESSERACT_PATH = find_tesseract_binary()
if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    tessdata_candidate = settings.tessdata_prefix or str(Path(TESSERACT_PATH).parent / "tessdata")
    if os.path.exists(tessdata_candidate):
        os.environ["TESSDATA_PREFIX"] = tessdata_candidate


# ============================================================
# FILE VALIDATION CONSTANTS & HELPERS
# ============================================================

MAGIC_BYTES = {
    ".pdf": b"%PDF-",
    ".png": b"\x89PNG\r\n\x1a\n",
    ".jpg": b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff"
}


def sanitize_filename(filename: str) -> str:
    """
    Prevents path traversal and cleans unsafe characters.
    """
    base = Path(filename).name
    # Keep alphanumeric, dashes, dots, underscores
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]", "_", base)
    return cleaned or "uploaded_file"


def validate_file_header(filename: str, content: bytes) -> Tuple[bool, str]:
    """
    Validates file extension, non-empty content, size, and magic bytes.
    """
    ext = Path(filename).suffix.lower()

    if ext not in settings.allowed_extensions:
        return False, f"Unsupported file type '{ext}'. Allowed: {', '.join(settings.allowed_extensions)}"

    if not content or len(content) == 0:
        return False, f"File '{filename}' is empty (0 bytes)."

    if len(content) > settings.max_file_size_bytes:
        size_mb = len(content) / (1024 * 1024)
        return False, f"File '{filename}' ({size_mb:.2f} MB) exceeds maximum limit of {settings.max_file_size_mb} MB."

    expected_magic = MAGIC_BYTES.get(ext)
    if expected_magic and not content.startswith(expected_magic):
        # Relaxed check for JPEG/JPG headers (some variants start with \xff\xd8)
        if ext in (".jpg", ".jpeg") and content.startswith(b"\xff\xd8"):
            return True, "Valid"
        return False, f"File '{filename}' content header does not match expected format for {ext}."

    return True, "Valid"


# ============================================================
# PDF DOCUMENT PROCESSING (PYMUPDF + OPTIONAL OCR)
# ============================================================

def extract_text_from_pdf(content: bytes, filename: str) -> Dict[str, Any]:
    """
    Extracts text page-by-page from PDF bytes using PyMuPDF.
    Detects scanned pages and applies OCR if Tesseract is available.
    """
    result = {
        "filename": filename,
        "type": "pdf",
        "status": "processed",
        "pages": 0,
        "extracted_chars": 0,
        "page_records": [],
        "error": None
    }

    try:
        doc = pymupdf.open(stream=content, filetype="pdf")

        if doc.is_encrypted:
            result["status"] = "error"
            result["error"] = "PDF document is password-protected or encrypted."
            return result

        result["pages"] = len(doc)

        for page_num in range(1, len(doc) + 1):
            page = doc[page_num - 1]
            text = page.get_text("text").strip()

            # If page text is very sparse (< 40 chars), attempt OCR if tesseract exists
            if len(text) < 40 and TESSERACT_PATH:
                try:
                    pix = page.get_pixmap(dpi=150)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    ocr_text = pytesseract.image_to_string(img).strip()
                    if len(ocr_text) > len(text):
                        text = ocr_text
                except Exception as ocr_err:
                    print(f"[OCR WARN] OCR failed on {filename} page {page_num}: {ocr_err}")

            cleaned_text = re.sub(r"[ \t]+", " ", text).strip()
            if cleaned_text:
                result["page_records"].append({
                    "page": page_num,
                    "text": cleaned_text
                })
                result["extracted_chars"] += len(cleaned_text)

        doc.close()

        if not result["page_records"]:
            result["status"] = "warning"
            result["error"] = "No readable text found in PDF (document may be scanned images without OCR)."

    except pymupdf.FileDataError as fde:
        result["status"] = "error"
        result["error"] = f"Corrupted or invalid PDF structure: {fde}"
    except Exception as err:
        result["status"] = "error"
        result["error"] = f"Failed to process PDF: {err}"

    return result


# ============================================================
# IMAGE PROCESSING (OCR VIA PYTESSERACT)
# ============================================================

def extract_text_from_image(content: bytes, filename: str) -> Dict[str, Any]:
    """
    Processes PNG, JPG, or JPEG images using PIL and Tesseract OCR.
    Handles environments where Tesseract binary is not installed.
    """
    result = {
        "filename": filename,
        "type": "image",
        "status": "processed",
        "pages": 1,
        "extracted_chars": 0,
        "page_records": [],
        "error": None
    }

    try:
        img = Image.open(io.BytesIO(content))
        img.verify()  # Validate image integrity

        # Re-open after verify
        img = Image.open(io.BytesIO(content))

        if TESSERACT_PATH:
            ocr_text = pytesseract.image_to_string(img).strip()
            cleaned_text = re.sub(r"[ \t]+", " ", ocr_text).strip()

            if cleaned_text:
                result["page_records"].append({
                    "page": 1,
                    "text": cleaned_text
                })
                result["extracted_chars"] = len(cleaned_text)
            else:
                result["status"] = "warning"
                result["error"] = "No readable text detected in image."
        else:
            result["status"] = "warning"
            result["error"] = "Tesseract OCR engine is not installed on host system. Image metadata was preserved."
            result["page_records"].append({
                "page": 1,
                "text": f"[Image file attached: {filename}. OCR engine not available on host system.]"
            })
            result["extracted_chars"] = len(result["page_records"][0]["text"])

    except Exception as err:
        result["status"] = "error"
        result["error"] = f"Corrupted or invalid image: {err}"

    return result


# ============================================================
# DOCUMENT CHUNKER (EPHEMERAL FOR RAG)
# ============================================================

def chunk_uploaded_documents(parsed_docs: List[Dict[str, Any]], chunk_size: int = 500) -> List[Dict[str, Any]]:
    """
    Chunks extracted document pages into isolated retrieval units with metadata.
    Does NOT write to ChromaDB. Kept ephemeral in memory.
    """
    chunks = []

    for doc_info in parsed_docs:
        filename = doc_info.get("filename", "unknown_document")
        doc_type = doc_info.get("type", "uploaded_document")

        for page_item in doc_info.get("page_records", []):
            page_num = page_item.get("page", 1)
            full_text = page_item.get("text", "")

            # Break page into word-based chunks of approximately chunk_size chars
            paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]
            if not paragraphs:
                paragraphs = [full_text]

            current_chunk = ""
            for p in paragraphs:
                if len(current_chunk) + len(p) <= chunk_size:
                    current_chunk += (" " if current_chunk else "") + p
                else:
                    if current_chunk:
                        chunks.append({
                            "source": filename,
                            "page": page_num,
                            "type": "uploaded_document",
                            "text": current_chunk.strip()
                        })
                    current_chunk = p

            if current_chunk:
                chunks.append({
                    "source": filename,
                    "page": page_num,
                    "type": "uploaded_document",
                    "text": current_chunk.strip()
                })

    return chunks

