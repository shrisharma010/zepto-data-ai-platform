import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from pydantic import ValidationError
from rag import retrieve
from schemas import AskResponse
from prompts import PROMPT

# Mock LLM is active by default unless explicitly set to '0'
MOCK = os.getenv("MOCK_LLM", "1") != "0"

KEYWORDS = [
    "delivery", "deliveries", "return", "refund", "membership",
    "tracking", "cancel", "gift card", "support hours", "perishable",
    "damaged", "missing", "fee", "zepto pass", "contact"
]

class State(TypedDict):
    query: str
    intent: str
    chunks: list
    answer: str
    sources: List[str]
    confidence: float

def classify_intent(state: State):
    if MOCK:
        q = state["query"].lower()
        intent = "policy_question" if any(k in q for k in KEYWORDS) else "general_question"
    else:
        from groq import Groq
        client = Groq()
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"Classify as 'policy_question' or 'general_question': {state['query']}"}],
            max_tokens=10
        )
        intent = resp.choices[0].message.content.strip().lower()
    return {"intent": intent}

def llm_answer(query: str, chunks: list):
    from groq import Groq
    client = Groq()
    context_str = "\n".join([f"[{c[0]}] {c[1]}" for c in chunks])
    prompt = PROMPT.format(context=context_str, question=query)

    for _ in range(3):  # 1 try + 2 retries
        raw = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        ).choices[0].message.content.strip()
        try:
            obj = AskResponse.model_validate_json(raw)
            return obj.answer, obj.confidence
        except ValidationError:
            prompt += "\n\nYour last output was invalid. Return ONLY valid JSON matching the schema."
    return "Error: could not produce a valid structured answer.", 0.0

def retrieve_and_answer(state: State):
    chunks = retrieve(state["query"], k=3)
    top_id, top_doc, _ = chunks[0]
    if MOCK:
        answer = f"Based on the retrieved context: {top_doc[:200]}"
        conf = 1.0
    else:
        answer, conf = llm_answer(state["query"], chunks)
    return {
        "chunks": chunks,
        "answer": answer,
        "sources": [c[0] for c in chunks],
        "confidence": conf
    }

def direct_answer(state: State):
    return {
        "answer": "I can only answer questions about Zepto policies right now.",
        "sources": [],
        "confidence": 1.0
    }

g = StateGraph(State)
g.add_node("classify_intent", classify_intent)
g.add_node("retrieve_and_answer", retrieve_and_answer)
g.add_node("direct_answer", direct_answer)

g.set_entry_point("classify_intent")
g.add_conditional_edges(
    "classify_intent",
    lambda s: "retrieve_and_answer" if s["intent"] == "policy_question" else "direct_answer",
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer"
    }
)
g.add_edge("retrieve_and_answer", END)
g.add_edge("direct_answer", END)

graph = g.compile()
