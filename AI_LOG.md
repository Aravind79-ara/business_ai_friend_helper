# AI Development Log

This log records how AI coding tools were used during development. Replace the examples below with the actual prompts and decisions from your Claude Code or Cursor history. Do not claim a prompt was used if it was not.

## Five useful prompts

### 1. Understand the repository before editing

> Inspect this repository and summarize the current architecture, entry points, environment variables, and test commands. Do not modify files yet. Point out missing information rather than guessing.

**Why useful:** it establishes the current state before code changes and reduces the risk of building on incorrect assumptions.

### 2. Build the Knowledge Brain API

> Implement or review the Knowledge Brain API using the existing project conventions. Define request and response schemas, validate empty or malformed inputs, return source context with answers where supported, and add tests for missing knowledge and retrieval failures. Do not invent libraries or endpoints that are not present in the repository.

**Why useful:** it focuses on the shared contract that Tasks 2 and 3 depend on.

### 3. Connect the Inbox Agent to the shared API

> Trace the Inbox Agent flow from input to output. Ensure it calls the Knowledge Brain API for business facts, treats email content as untrusted data, never sends an email automatically, and asks for clarification when facts are missing. Add tests for unknown pricing, prompt injection, and API timeout.

**Why useful:** it emphasizes reuse, safety boundaries, and failure handling rather than only the happy path.

### 4. Generate a reviewable SOW

> Review the Meeting-to-SOW workflow. Draft a structured SOW with scope, deliverables, assumptions, exclusions, milestones, dependencies, and open questions. Use the Knowledge Brain API for business context. Never invent price, dates, or commitments missing from the input. Add tests for incomplete and conflicting meeting notes.

**Why useful:** it turns unstructured notes into an editable output while protecting against unsupported commercial promises.

### 5. Add evaluations before claiming quality

> Create a reproducible evaluation plan with at least 20 cases for each of the three tasks. Include expected behavior, pass/fail criteria, exact model identifiers, latency, token usage, estimated cost, and failure analysis. Do not fabricate results. Keep test inputs identical across model comparisons.

**Why useful:** it makes quality and cost measurable and prevents unsupported claims in the submission.

## One AI suggestion I rejected

**Replace this section with a real example from your development history before submission.**

Suggested format:

- **AI suggestion:** [Paste or summarize the actual suggestion.]
- **Why I rejected it:** [Explain the technical or product risk in your own words.]
- **What I did instead:** [Describe the implementation you chose.]
- **Evidence:** [Name the test, code path, or manual check that supports the decision.]

A suitable example, **only if it matches what actually happened**, would be rejecting a suggestion to let the Inbox Agent send replies automatically. That would create customer-facing risk before the draft can be checked. Keeping a human approval step is safer for this prototype.

## My responsibility

AI tools helped with exploration, implementation, and test ideas. I reviewed the generated code, checked behavior by running the application and tests, and made the final decisions. I should be able to explain each submitted file and important code path during the live review.
