import glob
import os
import chromadb
from sentence_transformers import SentenceTransformer

# Load embedding model locally
model = SentenceTransformer("all-MiniLM-L6-v2")

# Persistent ChromaDB client
client = chromadb.PersistentClient(path="chroma_db")
col = client.get_or_create_collection("zepto_policies", metadata={"hnsw:space": "cosine"})

def ingest():
    if col.count() >= 8:
        return
    docs_pattern = os.path.join(os.path.dirname(__file__), "docs", "doc_*.txt")
    for path in sorted(glob.glob(docs_pattern)):
        doc_id = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
        col.add(
            ids=[doc_id],
            documents=[text],
            embeddings=[model.encode(text).tolist()],
            metadatas=[{"source": doc_id}]
        )

def retrieve(query, k=3):
    res = col.query(
        query_embeddings=[model.encode(query).tolist()],
        n_results=k
    )
    return list(zip(res["ids"][0], res["documents"][0], res["distances"][0]))

if __name__ == "__main__":
    ingest()
    print("Ingestion complete. Current count:", col.count())
