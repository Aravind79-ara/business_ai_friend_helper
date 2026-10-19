# AI Tech Consultant

AI Tech Consultant helps a small business turn its existing knowledge into useful, repeatable work. It connects three workflows: answering questions from business knowledge, processing incoming emails, and drafting a Statement of Work (SOW) from meeting notes.

## The three tasks

- **Knowledge Brain:** stores business information and retrieves relevant context for a question.
- **Inbox Agent:** uses the Knowledge Brain API to help classify and draft replies to business emails.
- **Meeting-to-SOW:** uses the Knowledge Brain API and meeting notes to draft a structured SOW for human review.

The shared knowledge layer reduces duplicated context and helps the workflows use the same business facts.

## Run locally

> Verify these commands against the current repository before submitting. Replace this section with the exact command that works from a clean clone.

```bash
git clone https://github.com/Aravind79-ara/business_ai_friend_helper.git
cd business_ai_friend_helper
# Install dependencies and configure environment variables as documented in the project.
# Start the complete application using the repository's one-command launcher.
```

If the repository uses Docker Compose, the intended one-command start may be:

```bash
docker compose up --build
```

Only keep that command if `docker-compose.yml` or `compose.yaml` exists and it starts all required services successfully.

## Configuration

1. Copy the example environment file (if provided) to `.env`.
2. Add required API keys and local configuration.
3. Never commit `.env`, passwords, access tokens, customer emails, or private business documents.
4. Use sample data for the demo.

## Verify

Run the project's documented automated tests and follow `EVALS.md` to reproduce the three task evaluations. The demo should show the happy path and at least one honest failure.

## Documentation

- [`DESIGN.md`](DESIGN.md): problem, architecture, choices, trade-offs, and next steps.
- [`EVALS.md`](EVALS.md): test cases and model evaluation protocol.
- [`AI_LOG.md`](AI_LOG.md): AI-assisted development record.

## Status and limitations

This repository is a capstone prototype, not a replacement for human approval. Generated email replies and SOWs must be reviewed before sending to a customer. Do not claim accuracy, latency, or cost results until they have been measured on the current code and recorded in `EVALS.md`.
