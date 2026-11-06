from pathlib import Path
import json
import re


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "Data" / "processed" / "documents.jsonl"
OUTPUT_FILE = PROJECT_ROOT / "Data" / "processed" / "chunks.jsonl"


# --------------------------------------------------
# Chunk settings
# --------------------------------------------------

CHUNK_SIZE = 700       # approximate number of words
CHUNK_OVERLAP = 100    # words shared between chunks


# --------------------------------------------------
# Text cleaning
# --------------------------------------------------

def clean_text(text: str) -> str:
    """
    Clean extracted PDF text while keeping useful information.
    """

    # Replace multiple spaces with one space
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


# --------------------------------------------------
# Split text into chunks
# --------------------------------------------------

def create_chunks(text: str):
    """
    Split text into overlapping word-based chunks.
    """

    words = text.split()

    if not words:
        return []

    chunks = []

    start = 0

    while start < len(words):

        end = min(start + CHUNK_SIZE, len(words))

        chunk_words = words[start:end]

        chunk_text = " ".join(chunk_words)

        chunks.append(chunk_text)

        # Stop when we reach the end
        if end >= len(words):
            break

        # Move forward while keeping overlap
        start = end - CHUNK_OVERLAP

    return chunks


# --------------------------------------------------
# Main processing
# --------------------------------------------------

def main():

    if not INPUT_FILE.exists():
        print("ERROR: documents.jsonl was not found.")
        print(f"Expected location: {INPUT_FILE}")
        return

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    total_documents = 0
    total_chunks = 0

    print("----------------------------------------")
    print("BIS SmartAssist - Chunking")
    print("----------------------------------------")

    with open(INPUT_FILE, "r", encoding="utf-8") as input_file, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:

        for line in input_file:

            if not line.strip():
                continue

            document = json.loads(line)

            total_documents += 1

            original_text = document.get("content", "")

            text = clean_text(original_text)

            if not text:
                continue

            chunks = create_chunks(text)

            for index, chunk_text in enumerate(chunks):

                chunk = {
                    "chunk_id": f"{document['source']}_page_{document['page']}_chunk_{index + 1}",

                    "content": chunk_text,

                    "source": document["source"],

                    "category": document["category"],

                    "page": document["page"],

                    "file_path": document["file_path"]
                }

                output_file.write(
                    json.dumps(chunk, ensure_ascii=False) + "\n"
                )

                total_chunks += 1

    print()
    print("----------------------------------------")
    print("Chunking completed successfully!")
    print("----------------------------------------")
    print(f"Input page records : {total_documents}")
    print(f"Output chunks      : {total_chunks}")
    print(f"Output file        : {OUTPUT_FILE}")
    print("----------------------------------------")


if __name__ == "__main__":
    main()