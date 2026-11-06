from pathlib import Path
import json


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DIR = PROJECT_ROOT / "Data" / "processed"

CHUNKS_FILE = PROCESSED_DIR / "chunks.jsonl"
STANDARDS_FILE = PROCESSED_DIR / "standards.jsonl"

OUTPUT_FILE = PROCESSED_DIR / "rag_documents.jsonl"


# ============================================================
# LOAD JSONL FILE
# ============================================================

def load_jsonl(file_path):
    """
    Load records from a JSONL file.
    """

    records = []

    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return records

    with open(file_path, "r", encoding="utf-8") as file:

        for line_number, line in enumerate(file, start=1):

            if not line.strip():
                continue

            try:
                record = json.loads(line)
                records.append(record)

            except json.JSONDecodeError as error:
                print(
                    f"Warning: Could not read line "
                    f"{line_number} in {file_path.name}: {error}"
                )

    return records


# ============================================================
# CONVERT PDF CHUNKS
# ============================================================

def convert_pdf_chunk(record, index):
    """
    Convert a PDF chunk into the unified RAG format.
    """

    chunk_id = record.get(
        "chunk_id",
        f"pdf_chunk_{index}"
    )

    content = record.get(
        "content",
        ""
    ).strip()

    metadata = {
        "source": record.get("source", ""),
        "category": record.get("category", ""),
        "page": record.get("page"),
        "file_path": record.get("file_path", ""),
        "source_type": "pdf"
    }

    return {
        "id": f"pdf_{index}_{chunk_id}",
        "text": content,
        "metadata": metadata
    }


# ============================================================
# CONVERT STANDARD RECORD
# ============================================================

def convert_standard(record, index):
    """
    Convert a structured BIS standard record
    into the unified RAG format.
    """

    standard_number = record.get(
        "standard_number",
        ""
    ).strip()

    year = record.get(
        "year",
        ""
    ).strip()

    title = record.get(
        "title",
        ""
    ).strip()

    status = record.get(
        "status",
        ""
    ).strip()

    # Use existing search_text when available.
    search_text = record.get(
        "search_text",
        ""
    ).strip()

    # Fallback if search_text is missing.
    if not search_text:

        search_text = (
            f"Standard Number: {standard_number}\n"
            f"Year: {year}\n"
            f"Title: {title}\n"
            f"Status: {status}"
        )

    metadata = {
        "source": record.get(
            "source",
            "BIS Standards Dataset"
        ),

        "source_file": record.get(
            "source_file",
            ""
        ),

        "category": "standards",

        "source_type": "structured_dataset",

        "standard_number": standard_number,

        "year": year,

        "status": status,

        "serial_no": record.get(
            "serial_no",
            ""
        )
    }

    return {
        "id": f"standard_{index}_{standard_number}",
        "text": search_text,
        "metadata": metadata
    }


# ============================================================
# REMOVE EMPTY RECORDS
# ============================================================

def remove_empty_records(records):

    cleaned = []

    for record in records:

        text = record.get(
            "text",
            ""
        ).strip()

        if text:

            cleaned.append(record)

    return cleaned


# ============================================================
# REMOVE DUPLICATE IDs
# ============================================================

def remove_duplicate_ids(records):

    unique = []
    seen_ids = set()

    duplicates = 0

    for record in records:

        record_id = record["id"]

        if record_id in seen_ids:

            duplicates += 1
            continue

        seen_ids.add(record_id)
        unique.append(record)

    return unique, duplicates


# ============================================================
# SAVE UNIFIED DATASET
# ============================================================

def save_jsonl(records):

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for record in records:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("BIS SmartAssist - Unified RAG Dataset")
    print("=" * 60)

    # --------------------------------------------------------
    # Load PDF chunks
    # --------------------------------------------------------

    print("\nLoading PDF chunks...")

    pdf_chunks = load_jsonl(
        CHUNKS_FILE
    )

    print(
        f"✓ PDF chunks loaded: "
        f"{len(pdf_chunks)}"
    )

    # --------------------------------------------------------
    # Load standards
    # --------------------------------------------------------

    print("\nLoading standards...")

    standards = load_jsonl(
        STANDARDS_FILE
    )

    print(
        f"✓ Standards loaded: "
        f"{len(standards)}"
    )

    # --------------------------------------------------------
    # Convert PDF chunks
    # --------------------------------------------------------

    print("\nConverting PDF chunks...")

    unified_pdf = []

    for index, record in enumerate(
        pdf_chunks,
        start=1
    ):

        converted = convert_pdf_chunk(
            record,
            index
        )

        unified_pdf.append(
            converted
        )

    print(
        f"✓ Converted PDF records: "
        f"{len(unified_pdf)}"
    )

    # --------------------------------------------------------
    # Convert standards
    # --------------------------------------------------------

    print("\nConverting standards...")

    unified_standards = []

    for index, record in enumerate(
        standards,
        start=1
    ):

        converted = convert_standard(
            record,
            index
        )

        unified_standards.append(
            converted
        )

    print(
        f"✓ Converted standard records: "
        f"{len(unified_standards)}"
    )

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    print("\nCombining datasets...")

    all_records = (
        unified_pdf +
        unified_standards
    )

    print(
        f"Total records before cleaning: "
        f"{len(all_records)}"
    )

    # --------------------------------------------------------
    # Remove empty records
    # --------------------------------------------------------

    all_records = remove_empty_records(
        all_records
    )

    print(
        f"Records after empty removal: "
        f"{len(all_records)}"
    )

    # --------------------------------------------------------
    # Remove duplicate IDs
    # --------------------------------------------------------

    all_records, duplicates = (
        remove_duplicate_ids(
            all_records
        )
    )

    print(
        f"Duplicate IDs removed: "
        f"{duplicates}"
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_jsonl(
        all_records
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("UNIFIED RAG DATASET CREATED SUCCESSFULLY")
    print("=" * 60)

    print(
        f"PDF records       : "
        f"{len(unified_pdf)}"
    )

    print(
        f"Standard records  : "
        f"{len(unified_standards)}"
    )

    print(
        f"Final records     : "
        f"{len(all_records)}"
    )

    print(
        f"Output file       : "
        f"{OUTPUT_FILE}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()