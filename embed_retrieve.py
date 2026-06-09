import json
import os
import subprocess
import sys

# ── Step 0: Run chunker.py if chunks.json doesn't exist ──────────────────────

CHUNKS_PATH = "chunks.json"
CHROMA_DIR  = "./chroma_db"

if not os.path.exists(CHUNKS_PATH):
    print("chunks.json not found — running chunker.py first...")
    result = subprocess.run([sys.executable, "chunker.py"], capture_output=False)
    if result.returncode != 0:
        print("ERROR: chunker.py failed. Fix it before continuing.")
        sys.exit(1)

with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    all_chunks = json.load(f)

print(f"Loaded {len(all_chunks)} chunks from {CHUNKS_PATH}\n")

# ── Step 1: Set up embedding model ───────────────────────────────────────────

print("Loading embedding model (all-MiniLM-L6-v2)...")
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded.\n")

# ── Step 2: Set up ChromaDB (persistent) ─────────────────────────────────────

import chromadb

client     = chromadb.PersistentClient(path=CHROMA_DIR)
COLLECTION = "csuf_food"

# Delete old collection so re-running this script stays idempotent
try:
    client.delete_collection(COLLECTION)
except Exception:
    pass

collection = client.create_collection(
    name=COLLECTION,
    metadata={"hnsw:space": "cosine"}   # cosine distance → scores 0–2; lower = closer
)

# ── Step 3: Embed + upsert all chunks ────────────────────────────────────────

print("Embedding and loading chunks into ChromaDB...")

ids         = []
embeddings  = []
documents   = []
metadatas   = []

for chunk in all_chunks:
    ids.append(chunk["chunk_id"])
    embeddings.append(model.encode(chunk["text"]).tolist())
    documents.append(chunk["text"])
    metadatas.append({
        "source":      chunk["source"],
        "url":         chunk.get("url", ""),
        "word_count":  chunk["word_count"],
        "chunk_index": int(chunk["chunk_id"].rsplit("_", 1)[-1])
    })

# Upsert in one batch (fast for small collections)
collection.upsert(
    ids=ids,
    embeddings=embeddings,
    documents=documents,
    metadatas=metadatas
)

print(f"Upserted {len(ids)} chunks → ChromaDB at {CHROMA_DIR}\n")

# ── Step 4: Retrieval function ────────────────────────────────────────────────

def retrieve(query: str, k: int = 5) -> list[dict]:
    """
    Returns top-k chunks for the query.
    Prints each result with its distance score and source.
    Distance uses cosine space: 0.0 = identical, 2.0 = opposite.
    Good matches typically score below 0.5.
    """
    q_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )

    docs      = results["documents"][0]
    metas     = results["metadatas"][0]
    distances = results["distances"][0]

    retrieved = []
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances)):
        entry = {"rank": i + 1, "distance": dist, "meta": meta, "text": doc}
        retrieved.append(entry)

        quality = "✅ Good" if dist < 0.5 else ("⚠️  Weak" if dist < 0.7 else "❌ Poor")
        print(f"  [{i+1}] {quality}  distance={dist:.3f}  source={meta['source']}")
        print(f"       {doc[:200].strip()}{'...' if len(doc) > 200 else ''}")
        print()

    return retrieved

# ── Step 5: Evaluation queries ───────────────────────────────────────────────
#
# These 5 queries reflect things a CSUF student would realistically ask.
# Adjust them to match whatever eval plan you wrote in planning.md.

EVAL_QUERIES = [
    "cheap sushi near CSUF",
    "good coffee shop to study near Cal State Fullerton",
    "vegan food options near CSUF",
    "authentic Mexican or Latin food near campus",
    "late night places to eat near Fullerton",
]

print("=" * 70)
print("RETRIEVAL EVALUATION — 5 QUERIES")
print("=" * 70)

for query in EVAL_QUERIES:
    print(f"\nQUERY: \"{query}\"")
    print("-" * 60)
    results = retrieve(query, k=5)

print("=" * 70)
print("Evaluation complete.")
print()
