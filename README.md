# AI Tech Consultant Capstone

This project implements a production-minded AI consultant for three connected workflows:
1. Knowledge Brain: product knowledge retrieval with citations and escalation
2. Inbox Agent: email triage and response drafting with reviewer approval gates
3. Meeting-to-Scope workflow: transcript analysis and proposal generation

## Quick start

1. Install Python 3.15 and create a virtual environment:
   `py -3.15 -m venv .venv`
2. Activate it and install the latest compatible dependencies:
   `.\.venv\Scripts\Activate.ps1`
   `python -m pip install --upgrade pip`
   `$env:PYYAML_FORCE_LIBYAML = "0"`
   `python -m pip install --upgrade -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in credentials.
4. Run the FastAPI app:
   `python -m uvicorn app.main:app --reload`
5. Run the Streamlit UI:
   `python -m streamlit run app/ui.py`
6. Run the tests:
   `python -m pytest`

The Knowledge Brain includes a conversational AI chat grounded in retrieved knowledge.
Set `OPENAI_API_KEY` in `.env` to enable live OpenAI responses. The default model is
`gpt-4.1-mini`; set `OPENAI_MODEL` to another model available to your API account if needed.
The OpenAI API key is
separate from a ChatGPT subscription and may incur API usage charges. Without an API key,
the chat clearly labels its response as retrieval-only. The chat API is available at
`POST /api/v1/chat` and accepts a `message` plus optional recent `history`.

Example request:

```json
{
  "message": "What should go into a project proposal?",
  "history": [
    {"role": "user", "content": "We just had a discovery meeting."},
    {"role": "assistant", "content": "What are the project goals?"}
  ]
}
```

The project requires Python 3.11 or newer; Python 3.15 is the recommended workspace
interpreter. Dependencies use lower bounds rather than fixed pins, so a fresh install
selects the newest versions compatible with the chosen Python interpreter.

## Project structure
- `app/` - application source code
- `data/` - SQLite database, evaluation datasets, and seed content
- `tests/` - automated tests and evaluation scripts
- `DESIGN.md` - architecture and planning artifacts

## Notes
Knowledge Brain chat uses the OpenAI API. When no OpenAI API key is configured, the app
shows a retrieval-only answer and clearly indicates that no live AI response was generated.
