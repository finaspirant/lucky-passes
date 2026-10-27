# Project Rules

- Use plain Python 3.11+ and the standard library, plus only the minimum needed (an HTTP client for the Meta Model API and pytest). Do not use LangChain, LangGraph, LlamaIndex, or other agent frameworks.
- Do not copy code from outside this repository. Write everything fresh during the event.
- Never commit secrets. Keep API keys in `.env` (gitignored), and maintain a committed `.env.example` with placeholders only.
- Use only Meta models for agent and judge calls.
- Log token counts for every model call.
- Keep files small and readable. Prefer simple code over clever code.
- I design first and write code myself unless I explicitly ask you to write it. When I ask for a design review, give feedback, not a full implementation.
