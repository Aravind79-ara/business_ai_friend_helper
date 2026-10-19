import pytest


@pytest.mark.parametrize(
    "question",
    [
        "How do I enable AI replies?",
        "Can a refund be processed automatically?",
        "What do I need to review before sending a quote?",
        "What should happen for security issues?",
        "How do I estimate project effort?",
        "What is the policy for cancellations?",
        "How should we handle high-risk categories?",
        "How can we explain the product?",
        "What does the proposal process include?",
        "Would a customer request a refund without human approval?",
        "What are the AI automation restrictions?",
        "How do I know when to escalate?",
        "What does safe automation mean?",
        "What should be in a proposal?",
        "Who approves a billing change?",
        "How do I configure the inbox AI?",
        "What happens after a lead requests a quote?",
        "What are functional requirements for proposal generation?",
        "Why are security issues treated differently?",
        "How quickly are refunds reviewed?",
    ],
)
def test_knowledge_brain_answers_and_cites_each_question(api_client, question):
    response = api_client.post("/api/v1/query", json={"question": question})

    assert response.status_code == 200
    result = response.json()
    assert result["status"] in {"answered", "insufficient evidence"}
    assert result["answer"].strip()
    assert result["request_id"]
    assert result["sources"]
    assert isinstance(result["human_escalation_required"], bool)
