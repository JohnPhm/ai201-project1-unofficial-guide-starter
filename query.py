"""
Generation layer — connects retrieval (ChromaDB) to Groq's LLM.

Run embed_retrieve.py once first to build ./chroma_db. This module then
connects to that existing collection (read-only) and exposes:
    retrieve(question, k)  -> top-k chunks from the vector store
    ask(question, k)       -> {"answer": str, "sources": [{source, url}, ...]}

Grounding is enforced by the system prompt + low temperature, and source
attribution is built programmatically from retrieval metadata — the LLM
never decides what to cite.
"""

import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq

# ── Config ───────────────────────────────────────────────────────────────────

load_dotenv()

CHROMA_DIR = "./chroma_db"
COLLECTION = "csuf_food"
EMBED_MODEL = "all-MiniLM-L6-v2"   # must match embed_retrieve.py
LLM_MODEL = "llama-3.3-70b-versatile"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY not found. Copy .env.example to .env and add your key "
        "(get a free one at https://console.groq.com)."
    )

# ── Load model + connect to existing collection ──────────────────────────────

print("Loading embedding model (all-MiniLM-L6-v2)...")
model = SentenceTransformer(EMBED_MODEL)

client = chromadb.PersistentClient(path=CHROMA_DIR)
try:
    collection = client.get_collection(COLLECTION)
except Exception:
    raise RuntimeError(
        f"Collection '{COLLECTION}' not found in {CHROMA_DIR}. "
        "Run `python embed_retrieve.py` first to build the vector store."
    )

groq_client = Groq(api_key=GROQ_API_KEY)
print(f"Connected to ChromaDB ({collection.count()} chunks) + Groq.\n")

# ── Grounding prompt ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You answer questions about food and dining options near California State "
    "University, Fullerton (CSUF), using ONLY the provided context. "
    "Do not use any outside or general knowledge. "
    "If the context does not contain enough information to answer the question, "
    'respond with exactly: "I don\'t have enough information to answer that." '
    "Keep answers concise and base every claim on the context provided."
)


# ── Retrieval ──────────────────────────────────────────────────────────────────

def retrieve(question: str, k: int = 5) -> list[dict]:
    """Return the top-k chunks for a question from the vector store."""
    q_embedding = model.encode(question).tolist()
    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    return [
        {"rank": i + 1, "distance": dist, "meta": meta, "text": doc}
        for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances))
    ]


# ── Generation ─────────────────────────────────────────────────────────────────

def ask(question: str, k: int = 5) -> dict:
    """
    Retrieve context, generate a grounded answer, and attach sources.

    Returns {"answer": str, "sources": [{"source": str, "url": str}, ...]}.
    Sources are derived from retrieval metadata, NOT parsed from the model
    output, so attribution is guaranteed regardless of what the LLM says.
    """
    hits = retrieve(question, k)

    if not hits:
        return {"answer": "I don't have enough information to answer that.",
                "sources": []}

    context = "\n\n".join(
        f"[Source: {h['meta']['source']}]\n{h['text']}" for h in hits
    )

    response = groq_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.2,   # low → stays close to the retrieved context
    )
    answer = response.choices[0].message.content.strip()

    # Programmatic source attribution: de-duplicate by source name, keep order.
    seen = set()
    sources = []
    for h in hits:
        src = h["meta"]["source"]
        if src not in seen:
            seen.add(src)
            sources.append({"source": src, "url": h["meta"].get("url", "")})

    return {"answer": answer, "sources": sources}


# ── End-to-end test on the planning.md eval questions ────────────────────────

if __name__ == "__main__":
    test_questions = [
        "How much does the CSUF dining plan cost?",
        "What is a good spot for cheap sushi near Fullerton?",
        "What do reviewers say about the Gastronome?",
        # A question the documents should NOT be able to answer — tests grounding:
        "What is the best ramen restaurant in Tokyo?",
    ]

    print("=" * 70)
    print("GROUNDED GENERATION TEST")
    print("=" * 70)
    for q in test_questions:
        result = ask(q)
        print(f"\nQ: {q}")
        print(f"A: {result['answer']}")
        print("Sources: " + ", ".join(s["source"] for s in result["sources"]))
        print("-" * 70)
