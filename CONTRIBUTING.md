# Contributing

Thanks for taking an interest in Weather MCP.

## Development Setup

Install backend dependencies:

```bash
uv sync
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

## Local Checks

Run backend tests:

```bash
uv run python -m unittest discover -s tests -v
```

Build the frontend:

```bash
cd frontend
npm run build
```

## Pull Requests

- Keep changes focused and easy to review.
- Add or update tests when behavior changes.
- Update documentation when commands, APIs, or architecture change.
- Prefer small commits with clear messages.

## Commit Style

This project uses concise conventional-style commit messages:

```text
feat: add hourly forecast endpoint
fix: handle unsupported forecast locations
docs: document local development
test: cover alert validation
```
