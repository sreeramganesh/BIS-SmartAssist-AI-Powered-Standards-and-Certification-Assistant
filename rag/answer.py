from pathlib import Path

import requests
import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# BIS SmartAssist - RAG Answer Engine
# ChromaDB + Sentence Transformers + Ollama Llama
# ============================================================


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_PATH = PROJECT_ROOT / "chroma_db"


# ============================================================
# SETTINGS
# ============================================================

COLLECTION_NAME = "bis_smartassist"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"

TOP_K = 5

# ChromaDB cosine-distance threshold.
# Lower distance = better match.
RELEVANCE_THRESHOLD = 0.90


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

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
# SEARCH BIS KNOWLEDGE BASE
# ============================================================

def search_bis(question, top_k=TOP_K):

    question_embedding = embedding_model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    return documents, metadatas, distances


# ============================================================
# FILTER RELEVANT RESULTS
# ============================================================

def filter_relevant_results(
    documents,
    metadatas,
    distances,
    threshold=RELEVANCE_THRESHOLD
):

    filtered_documents = []
    filtered_metadatas = []
    filtered_distances = []

    for i, distance in enumerate(distances):

        if distance <= threshold:

            filtered_documents.append(
                documents[i]
            )

            filtered_metadatas.append(
                metadatas[i]
            )

            filtered_distances.append(
                distance
            )

    return (
        filtered_documents,
        filtered_metadatas,
        filtered_distances
    )


# ============================================================
# EVIDENCE SCORE
# ============================================================

def calculate_evidence_score(distances):
    """
    Application-level evidence score based on ChromaDB retrieval.
    This is NOT Llama's self-reported confidence.
    Lower Chroma distance means a stronger semantic match.
    """
    if not distances:
        return 0

    best_distance = min(distances)
    score = (1 - best_distance) * 100
    return round(max(0, min(100, score)))


def get_evidence_message(score):
    if score >= 80:
        return "Strong supporting evidence found in the BIS knowledge base."
    elif score >= 60:
        return "Moderate supporting evidence found. Verify the cited BIS sources."
    else:
        return "Limited supporting evidence. Official BIS verification is recommended."


# ============================================================
# GENERATE ANSWER USING OLLAMA
# ============================================================

def generate_answer(
    question,
    documents,
    metadatas
):

    context_parts = []

    for i, document in enumerate(documents):

        metadata = (
            metadatas[i]
            if i < len(metadatas)
            else {}
        )

        source = metadata.get(
            "source",
            "BIS Knowledge Base"
        )

        page = metadata.get(
            "page",
            "N/A"
        )

        category = metadata.get(
            "category",
            "BIS"
        )

        standard_number = metadata.get(
            "standard_number",
            ""
        )

        year = metadata.get(
            "year",
            ""
        )

        status = metadata.get(
            "status",
            ""
        )

        context_parts.append(
            f"""
SOURCE {i + 1}

Category: {category}
Source: {source}
Page: {page}
Standard: {standard_number}
Year: {year}
Status: {status}

Content:
{document}
"""
        )

    context = "\n".join(context_parts)


    # ========================================================
    # RAG PROMPT
    # ========================================================

    prompt = f"""
You are BIS SmartAssist, an AI assistant specialized in
Bureau of Indian Standards (BIS) information.

Answer ONLY using the provided BIS knowledge-base context.

IMPORTANT RULES:
1. Do not invent BIS requirements.
2. Do not use outside or general knowledge.
3. If the context is insufficient, say:
   "I could not find sufficient information in the BIS knowledge base to answer this accurately."
4. Mention Indian Standards only when supported by the context.
5. Mention certification, testing, or documentation requirements only when supported.
6. Do not claim that a product is certified or compliant.
7. This assistant provides guidance only.
8. Do not generate an Evidence Score. Python calculates it separately.
9. Do not invent URLs, clauses, page numbers, document names, or requirements.

FORMAT:

PRODUCT / QUERY
Briefly identify the product or subject.

APPLICABLE INDIAN STANDARDS
List only relevant standards supported by the context.
For each one include:
- Standard number
- Standard title
- Status, if available

CERTIFICATION
Explain only what is supported.
If unavailable:
"Not available in the retrieved BIS information."

TESTING
Explain only what is supported.
If unavailable:
"Not available in the retrieved BIS information."

DOCUMENTATION
Explain only what is supported.
If unavailable:
"Not available in the retrieved BIS information."

IMPORTANT NOTES
Mention important limitations or conditions supported by the context.

SOURCE SUMMARY
Briefly identify the retrieved source(s) used.
Do not invent source details.

USER QUESTION:
{question}

BIS KNOWLEDGE BASE CONTEXT:
{context}

Now provide a clear, simple, structured, source-backed answer.
"""


    # ========================================================
    # CALL OLLAMA
    # ========================================================

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]


# ============================================================
# DISPLAY SOURCES
# ============================================================
def display_sources(metadatas, distances):

    print("\n" + "=" * 70)
    print("SUPPORTING BIS SOURCES")
    print("=" * 70)

    seen = set()
    source_number = 1

    for i, metadata in enumerate(metadatas):

        source = metadata.get(
            "source",
            "BIS Knowledge Base"
        )

        page = metadata.get(
            "page",
            "N/A"
        )

        category = metadata.get(
            "category",
            "BIS"
        )

        standard_number = metadata.get(
            "standard_number",
            ""
        )

        source_key = (
            source,
            page,
            standard_number
        )

        if source_key in seen:
            continue

        seen.add(source_key)

        distance = (
            distances[i]
            if i < len(distances)
            else None
        )

        print(f"\nSource {source_number}")
        print(f"Source   : {source}")
        print(f"Category : {category}")
        print(f"Page     : {page}")

        if standard_number:
            print(f"Standard : {standard_number}")

        if metadata.get("year"):
            print(f"Year     : {metadata.get('year')}")

        if metadata.get("status"):
            print(f"Status   : {metadata.get('status')}")

        if distance is not None:
            print(f"Distance : {distance:.4f}")

        source_number += 1


# ============================================================
# DISPLAY EVIDENCE SCORE
# ============================================================

def display_evidence_score(distances):

    score = calculate_evidence_score(distances)

    print("\n" + "=" * 70)
    print("EVIDENCE SCORE")
    print("=" * 70)

    print(f"\n{score} / 100")
    print(get_evidence_message(score))

    print(
        "\nNote: This score represents retrieval evidence "
        "from the BIS knowledge base; it is not Llama's "
        "self-reported confidence."
    )

    return score


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("BIS SMARTASSIST - AI RAG ASSISTANT")
    print("=" * 70)

    print("\nType your BIS question.")
    print("Type 'exit' to stop.")

    while True:

        question = input("\nYou: ").strip()

        if question.lower() == "exit":

            print("\nGoodbye!")
            break

        if not question:
            print("Please enter a question.")
            continue

        try:

            # ==================================================
            # STEP 1: SEARCH
            # ==================================================

            print(
                "\nSearching BIS Knowledge Base..."
            )

            (
                documents,
                metadatas,
                distances
            ) = search_bis(question)

            if not documents:

                print(
                    "\n⚠ No BIS information found."
                )

                continue


            # ==================================================
            # STEP 2: FILTER
            # ==================================================

            (
                relevant_documents,
                relevant_metadatas,
                relevant_distances
            ) = filter_relevant_results(
                documents,
                metadatas,
                distances
            )


            # ==================================================
            # STEP 3: CHECK RELEVANCE
            # ==================================================

            if not relevant_documents:

                print(
                    "\n⚠ No sufficiently relevant BIS "
                    "information found."
                )

                print(
                    f"\nRelevance threshold: "
                    f"{RELEVANCE_THRESHOLD}"
                )

                print(
                    "\nThe query may be outside the "
                    "available BIS knowledge base."
                )

                continue


            print(
                f"\n✓ Relevant BIS records found: "
                f"{len(relevant_documents)}"
            )


            # ==================================================
            # STEP 4: GENERATE ANSWER
            # ==================================================

            print(
                "\nGenerating answer using Llama..."
            )

            answer = generate_answer(
                question,
                relevant_documents,
                relevant_metadatas
            )


            # ==================================================
            # STEP 5: DISPLAY ANSWER
            # ==================================================

            print("\n" + "=" * 70)
            print("BIS SMARTASSIST - ANSWER")
            print("=" * 70)

            print("\n" + answer)


            # ==================================================
            # STEP 6: DISPLAY EVIDENCE SCORE
            # ==================================================

            display_evidence_score(
                relevant_distances
            )


            # ==================================================
            # STEP 7: DISPLAY SOURCES
            # ==================================================

            display_sources(
                relevant_metadatas,
                relevant_distances
            )

            print("\n" + "-" * 70)
            print("⚠ This answer is guidance only.")
            print(
                "Verify current requirements with official "
                "BIS sources before making compliance decisions."
            )


        except requests.exceptions.ConnectionError:

            print(
                "\n❌ Cannot connect to Ollama."
            )

            print(
                "Make sure Ollama is running."
            )


        except requests.exceptions.Timeout:

            print(
                "\n❌ Ollama took too long to respond."
            )


        except Exception as e:

            print("\n❌ Error:")
            print(e)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()