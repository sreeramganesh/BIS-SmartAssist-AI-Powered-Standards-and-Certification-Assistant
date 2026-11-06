from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_PATH = PROJECT_ROOT / "chroma_db"


# ============================================================
# SETTINGS
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"

COLLECTION_NAME = "bis_smartassist"

# Number of candidates retrieved from ChromaDB
TOP_K = 5

# Maximum acceptable ChromaDB distance.
# Lower distance = more similar.
#
# This is an initial value and can be tuned later
# using a larger test set.
RELEVANCE_THRESHOLD = 0.90


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("✓ Embedding model loaded.")


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

print("Connecting to ChromaDB...")

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

collection = client.get_collection(
    name=COLLECTION_NAME
)

print("✓ Connected to ChromaDB.")
print(f"✓ Records available: {collection.count()}")


# ============================================================
# SEARCH FUNCTION
# ============================================================

def search_bis(query, top_k=TOP_K):

    # --------------------------------------------------------
    # Convert user question into an embedding
    # --------------------------------------------------------

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    ).tolist()


    # --------------------------------------------------------
    # Search ChromaDB
    # --------------------------------------------------------

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )


    # --------------------------------------------------------
    # Extract results
    # --------------------------------------------------------

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]


    # --------------------------------------------------------
    # Filter results using relevance threshold
    # --------------------------------------------------------

    filtered_documents = []
    filtered_metadatas = []
    filtered_distances = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        # Lower distance = better semantic match
        if distance <= RELEVANCE_THRESHOLD:

            filtered_documents.append(document)
            filtered_metadatas.append(metadata)
            filtered_distances.append(distance)


    # --------------------------------------------------------
    # Return results in the same format expected by
    # answer.py
    # --------------------------------------------------------

    return {
        "documents": [filtered_documents],
        "metadatas": [filtered_metadatas],
        "distances": [filtered_distances]
    }


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(query, results):

    print("\n")
    print("=" * 70)
    print("BIS SMARTASSIST - SEARCH RESULTS")
    print("=" * 70)

    print(f"\nQuery: {query}")

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]


    # --------------------------------------------------------
    # No relevant results
    # --------------------------------------------------------

    if not documents:

        print("\n⚠ No sufficiently relevant BIS information found.")

        print(
            f"\nRelevance threshold: "
            f"{RELEVANCE_THRESHOLD}"
        )

        print(
            "\nThe query may be outside the available "
            "BIS knowledge base."
        )

        return


    # --------------------------------------------------------
    # Display filtered results
    # --------------------------------------------------------

    print(
        f"\n✓ Relevant results found: "
        f"{len(documents)}"
    )


    for i, document in enumerate(documents):

        metadata = metadatas[i]
        distance = distances[i]


        print("\n" + "-" * 70)

        print(f"RESULT {i + 1}")

        print("-" * 70)


        # ----------------------------------------------------
        # Source
        # ----------------------------------------------------

        print(
            f"Source    : "
            f"{metadata.get('source', 'Unknown')}"
        )


        # ----------------------------------------------------
        # Category
        # ----------------------------------------------------

        print(
            f"Category  : "
            f"{metadata.get('category', 'Unknown')}"
        )


        # ----------------------------------------------------
        # Page
        # ----------------------------------------------------

        if metadata.get("page") is not None:

            print(
                f"Page      : "
                f"{metadata.get('page')}"
            )


        # ----------------------------------------------------
        # Standard number
        # ----------------------------------------------------

        if metadata.get("standard_number"):

            print(
                f"Standard  : "
                f"{metadata.get('standard_number')}"
            )


        # ----------------------------------------------------
        # Year
        # ----------------------------------------------------

        if metadata.get("year"):

            print(
                f"Year      : "
                f"{metadata.get('year')}"
            )


        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        if metadata.get("status"):

            print(
                f"Status    : "
                f"{metadata.get('status')}"
            )


        # ----------------------------------------------------
        # Distance
        # ----------------------------------------------------

        print(
            f"Distance  : "
            f"{distance:.4f}"
        )


        # ----------------------------------------------------
        # Relevant information
        # ----------------------------------------------------

        print("\nRelevant Information:")

        print(document[:1500])


        if len(document) > 1500:

            print(
                "\n[Content truncated for display]"
            )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("BIS SmartAssist - Semantic Search")
    print("=" * 70)

    print("\nType your BIS question.")
    print("Type 'exit' to stop.")


    while True:

        query = input("\nYou: ").strip()


        # ----------------------------------------------------
        # Exit
        # ----------------------------------------------------

        if query.lower() == "exit":

            print("\nSearch stopped.")

            break


        # ----------------------------------------------------
        # Empty query
        # ----------------------------------------------------

        if not query:

            print("Please enter a question.")

            continue


        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        print("\nSearching BIS Knowledge Base...")


        results = search_bis(
            query,
            TOP_K
        )


        # ----------------------------------------------------
        # Display
        # ----------------------------------------------------

        display_results(
            query,
            results
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()