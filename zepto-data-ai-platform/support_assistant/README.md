# Module 3: Customer Support Assistant

## Architecture Overview
The support assistant is built as a retrieval-augmented generation (RAG) agent using FastAPI, LangGraph, SentenceTransformers, and ChromaDB:

```text
docs/*.txt ---> ingest() in rag.py (SentenceTransformer all-MiniLM-L6-v2) ---> ChromaDB ("zepto_policies")
                                                                                    |
POST /ask ---> classify_intent ---> [policy_question] ---> retrieve_and_answer <----+
                               ---> [general_question] ---> direct_answer
```

- **Ingestion (`rag.py`)**: Reads the 8 policy documents from `docs/` and embeds them using `all-MiniLM-L6-v2`.
- **Storage**: Persistent ChromaDB collection `zepto_policies` using cosine similarity (`hnsw:space: cosine`).
- **State Graph Routing (`graph.py`)**: LangGraph evaluates intent (`policy_question` vs `general_question`) using keyword heuristics in mock mode or Groq LLM when configured.
- **Mock vs. Real Mode**: Controlled via `MOCK_LLM` (defaults to active `1`). When `MOCK_LLM=0`, queries Groq `llama-3.3-70b-versatile` with prompt formatting and up to 2 JSON validation retries.

## Recorded API Calls (MOCK_LLM=1)

### Policy Query:
```bash
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"query": "How long does a refund take?"}'
```
**Response:**
```json
{
  "answer": "Based on the retrieved context: Refunds for eligible items are processed immediately back to the original payment method upon approval. Depending on your bank, credit/debit card refunds may take 3 to 5 business days to reflect. UPI ref",
  "sources": ["doc_02", "doc_06", "doc_05"],
  "confidence": 1.0
}
```

### General Query:
```bash
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"query": "What is the capital of France?"}'
```
**Response:**
```json
{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}
```

## Running the App
```powershell
uvicorn support_assistant.main:app --port 8000
```