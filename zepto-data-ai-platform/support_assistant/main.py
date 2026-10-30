import sys
from pathlib import Path

# Allow `uvicorn support_assistant.main:app` from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI
from schemas import AskRequest, AskResponse
from graph import graph
from rag import ingest

app = FastAPI(title="Zepto Support Assistant")

@app.on_event("startup")
def _startup():
    ingest()

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    out = graph.invoke({"query": req.query})
    return AskResponse(
        answer=out["answer"],
        sources=out.get("sources", []),
        confidence=out.get("confidence", 1.0)
    )
