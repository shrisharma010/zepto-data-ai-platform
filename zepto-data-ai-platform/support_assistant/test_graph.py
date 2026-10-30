from graph import graph
from rag import ingest

def test_support_assistant():
    ingest()
    
    # Test 1: Policy question routing and retrieval
    res_policy = graph.invoke({"query": "How long does a refund take?"})
    assert res_policy["intent"] == "policy_question"
    assert "doc_02" in res_policy["sources"]
    assert res_policy["answer"].startswith("Based on the retrieved context:")
    
    # Test 2: General question fallback
    res_general = graph.invoke({"query": "What is the capital of France?"})
    assert res_general["intent"] == "general_question"
    assert res_general["sources"] == []
    assert res_general["answer"] == "I can only answer questions about Zepto policies right now."

    print("All LangGraph unit tests passed successfully!")

if __name__ == "__main__":
    test_support_assistant()
