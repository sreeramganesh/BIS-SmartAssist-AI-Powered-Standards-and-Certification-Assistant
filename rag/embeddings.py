from pathlib import Path
import json

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "Data"
    / "processed"
    / "rag_documents.jsonl"
)

CHROMA_PATH = PROJECT_ROOT / "chroma_db"


# ============================================================
# SETTINGS
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"

COLLECTION_NAME = "bis_smartassist"

BATCH_SIZE = 64


# ============================================================
# LOAD RAG DOCUMENTS
# ============================================================

def load_documents():

    documents = []

    if not INPUT_FILE.exists():

        print(
            f"ERROR: File not found:\n{INPUT_FILE}"
        )

        return documents

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        for line_number, line in enumerate(
            file,
            start=1
        ):

            if not line.strip():
                continue

            try:

                record = json.loads(line)

                text = record.get(
                    "text",
                    ""
                ).strip()

                record_id = record.get(
                    "id",
                    ""
                ).strip()

                if not text or not record_id:
                    continue

                documents.append(record)

            except json.JSONDecodeError as error:

                print(
                    f"Warning: Invalid JSON at line "
                    f"{line_number}: {error}"
                )

    return documents


# ============================================================
# CLEAN METADATA FOR CHROMA
# ============================================================

def clean_metadata(metadata):

    cleaned = {}

    for key, value in metadata.items():

        # Chroma metadata values should not be None
        if value is None:
            continue

        # Convert values to supported simple types
        if isinstance(value, (str, int, float, bool)):

            cleaned[key] = value

        else:

            cleaned[key] = str(value)

    return cleaned


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("BIS SmartAssist - Embeddings + ChromaDB")
    print("=" * 60)

    # --------------------------------------------------------
    # Load documents
    # --------------------------------------------------------

    print("\nLoading RAG documents...")

    records = load_documents()

    if not records:

        print("ERROR: No RAG documents found.")
        return

    print(
        f"✓ RAG documents loaded: {len(records)}"
    )

    # --------------------------------------------------------
    # Load embedding model
    # --------------------------------------------------------

    print("\nLoading embedding model...")

    print(
        f"Model: {MODEL_NAME}"
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    print("✓ Embedding model loaded.")

    # --------------------------------------------------------
    # Create Chroma client
    # --------------------------------------------------------

    print("\nCreating ChromaDB...")

    CHROMA_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    # --------------------------------------------------------
    # Create / reset collection
    # --------------------------------------------------------

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description":
                "BIS SmartAssist knowledge base"
        }
    )

    # --------------------------------------------------------
    # Prepare data
    # --------------------------------------------------------

    ids = []
    texts = []
    metadatas = []

    for record in records:

        ids.append(
            record["id"]
        )

        texts.append(
            record["text"]
        )

        metadatas.append(
            clean_metadata(
                record.get(
                    "metadata",
                    {}
                )
            )
        )

    # --------------------------------------------------------
    # Generate embeddings in batches
    # --------------------------------------------------------

    total = len(texts)

    print(
        f"\nGenerating embeddings for "
        f"{total} records..."
    )

    for start in range(
        0,
        total,
        BATCH_SIZE
    ):

        end = min(
            start + BATCH_SIZE,
            total
        )

        batch_texts = texts[start:end]

        batch_ids = ids[start:end]

        batch_metadatas = metadatas[start:end]

        print(
            f"Processing "
            f"{start + 1}-{end} "
            f"of {total}..."
        )

        embeddings = model.encode(
            batch_texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            normalize_embeddings=True
        )

        collection.upsert(
            ids=batch_ids,
            documents=batch_texts,
            embeddings=embeddings.tolist(),
            metadatas=batch_metadatas
        )

    # --------------------------------------------------------
    # Verify collection
    # --------------------------------------------------------

    final_count = collection.count()

    print("\n" + "=" * 60)
    print("EMBEDDING + CHROMADB COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print(
        f"Documents processed : {total}"
    )

    print(
        f"Chroma records      : {final_count}"
    )

    print(
        f"Chroma database     : {CHROMA_PATH}"
    )

    print(
        f"Collection          : {COLLECTION_NAME}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()