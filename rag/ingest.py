from pathlib import Path
import json
import fitz  # PyMuPDF

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA = PROJECT_ROOT / "Data" / "raw"
PROCESSED_DATA = PROJECT_ROOT / "Data" / "processed"

OUTPUT_FILE = PROCESSED_DATA / "documents.jsonl"


def get_category(pdf_path: Path) -> str:
    """
    Get the category from the folder name.
    Example:
    Data/raw/certification/file.pdf
    -> certification
    """
    return pdf_path.parent.name


def extract_pdf(pdf_path: Path):
    """
    Extract text from a PDF page by page.
    """

    documents = []

    try:
        pdf = fitz.open(pdf_path)

        for page_number, page in enumerate(pdf, start=1):

            text = page.get_text("text").strip()

            # Skip empty pages
            if not text:
                continue

            document = {
                "content": text,
                "source": pdf_path.name,
                "category": get_category(pdf_path),
                "page": page_number,
                "file_path": str(pdf_path.relative_to(PROJECT_ROOT))
            }

            documents.append(document)

        pdf.close()

    except Exception as e:
        print(f"ERROR reading {pdf_path.name}: {e}")

    return documents


def main():

    # Create processed directory if it doesn't exist
    PROCESSED_DATA.mkdir(parents=True, exist_ok=True)

    all_documents = []

    # Find every PDF inside Data/raw/
    pdf_files = list(RAW_DATA.rglob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF files.")

    for pdf_file in pdf_files:

        print(f"Processing: {pdf_file.name}")

        documents = extract_pdf(pdf_file)

        all_documents.extend(documents)

        print(f"  → Extracted {len(documents)} pages")

    # Save as JSONL
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

        for document in all_documents:
            file.write(json.dumps(document, ensure_ascii=False) + "\n")

    print("\n--------------------------------")
    print("PDF ingestion completed!")
    print(f"Total pages extracted: {len(all_documents)}")
    print(f"Output file: {OUTPUT_FILE}")
    print("--------------------------------")


if __name__ == "__main__":
    main()