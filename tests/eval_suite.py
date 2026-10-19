from __future__ import annotations

from app.bootstrap import init_db
from app.services.inbox_agent import classify_email
from app.services.knowledge_brain import answer_question, ensure_seed_documents
from app.services.meeting_agent import process_meeting


def evaluate_task_1():
    questions = [
        "How do I enable AI assistant replies?",
        "What is the refund policy?",
        "Who approves a cancellation?",
        "How do I estimate scope?",
        "What should happen for security cases?",
        "What happens after a quote request?",
        "How do I configure low-risk automation?",
        "What is the requirement for human review?",
        "Can a refund be sent automatically?",
        "What is included in a proposal?",
        "How should billing changes be reviewed?",
        "What is the safe automation rule?",
        "What do I do if the knowledge base is missing evidence?",
        "Who handles account security cases?",
        "What is the policy for sales proposals?",
        "When is AI automation approved?",
        "How do I revisit the proposal estimate?",
        "Why are high-risk categories escalated?",
        "What should happen before sending a refund message?",
        "Why use a human approval step?",
        "How quickly are refunds reviewed?",
        "What are the advice guidelines for response drafting?",
        "Which categories are risky?",
        "What does a secure workflow require?",
        "How do we explain the proposal process?",
    ]
    scores = []
    for question in questions:
        result = answer_question(question)
        score = 1 if result["status"] in {"answered", "insufficient evidence"} else 0
        scores.append(score)
    return {"task": "task_1", "cases": len(scores), "mean_score": sum(scores) / len(scores), "scores": scores}


def evaluate_task_2():
    emails = [
        ("How do I enable AI replies?", "product_how_to"),
        ("I need a refund", "refunds_and_cancellations"),
        ("My account is locked", "account_security"),
        ("I need a quote", "quote_request"),
        ("The feature is broken", "technical_troubleshooting"),
        ("I want to cancel my subscription", "refunds_and_cancellations"),
        ("Can we build an AI assistant?", "project_request"),
        ("The billing screen fails", "technical_troubleshooting"),
        ("I have a security issue", "account_security"),
        ("Where is the AI settings page?", "product_how_to"),
        ("What is the price for a new automation project?", "quote_request"),
        ("My account was hacked", "account_security"),
        ("Please cancel my plan", "refunds_and_cancellations"),
        ("I need a project estimate", "quote_request"),
        ("The tool keeps failing", "technical_troubleshooting"),
        ("We need a proposal", "quote_request"),
        ("How do I set up a support bot?", "product_how_to"),
        ("We want an AI onboarding pilot", "project_request"),
        ("This is unacceptable", "complaint"),
        ("How to use support knowledge?", "product_how_to"),
        ("I think someone changed my password", "account_security"),
        ("Can I get a refund today?", "refunds_and_cancellations"),
        ("I need a budget estimate", "quote_request"),
        ("The login button is broken", "technical_troubleshooting"),
        ("Can you help me set up automation?", "product_how_to"),
    ]
    scores = []
    for subject, expected in emails:
        category, _ = classify_email(subject, subject)
        score = 1 if category == expected else 0
        scores.append(score)
    return {"task": "task_2", "cases": len(scores), "mean_score": sum(scores) / len(scores), "scores": scores}


def evaluate_task_3():
    transcripts = [
        "We need an AI support assistant that reads documentation before drafting replies.",
        "We want project estimates and a proposal template for client work.",
        "We need a review step for account security and billing changes.",
        "The workflow should automate low-risk how-to questions while keeping refunds manual.",
        "We need proposal generation for a support ticket automation rollout.",
        "The support team requires knowledge retrieval and email triage.",
        "We need a workflow to process account issues and maintain security review.",
        "The product needs a proposal generator after the discovery call.",
        "We need AI assistance for support inbox triage and escalation.",
        "We want to classify incoming emails and isolate high-risk cases.",
        "The system needs proposal estimation and implementation planning.",
        "We need to handle knowledge questions and customer follow-ups.",
        "Project requirements include AI automation and human review.",
        "The client wants project estimates and clear scope boundaries.",
        "We need support workflow automation and account access review.",
        "We need to automate informational answers but keep refund work manual.",
        "The project should generate proposals and summary notes.",
        "We need secure handling of password resets and access issues.",
        "We want to triage emails and prepare a business proposal.",
        "Our goal is to estimate effort for a AI support and review system.",
        "We need support for customer documentation, email triage, and follow-up.",
        "The system should not auto-send sensitive billing or security decisions.",
        "We need an operation to draft client-ready proposals from transcripts.",
        "We need a meeting-to-scope workflow for technical consulting work.",
        "The solution should recommend a review layer for security and billing requests.",
    ]
    scores = []
    for transcript in transcripts:
        result = process_meeting("Discovery meeting", transcript, "Client")
        score = 1 if result["status"] == "completed" and result["estimate_hours"] > 0 else 0
        scores.append(score)
    return {"task": "task_3", "cases": len(scores), "mean_score": sum(scores) / len(scores), "scores": scores}


def compare_model_configs():
    configs = [
        {"name": "gpt-4.1-mini"},
        {"name": "gpt-4.1"},
    ]
    return configs


def main():
    init_db()
    ensure_seed_documents()
    results = [
        evaluate_task_1(),
        evaluate_task_2(),
        evaluate_task_3(),
        {"task": "model_comparison", "results": compare_model_configs()},
    ]
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
