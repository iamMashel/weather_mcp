# Weather MCP

A small full-stack weather application that exposes National Weather Service data through an MCP server, a FastAPI bridge, and a Nuxt frontend.

## Features

- MCP tools for active alerts and short-range forecasts
- FastAPI endpoints for browser and frontend clients
- Structured JSON responses for forecasts and alerts
- Nuxt UI with forecast cards, alert severity styling, loading states, and validation
- Backend tests that mock upstream weather calls

## Architecture

```text
Nuxt frontend
  -> FastAPI REST API
    -> Weather service functions
      -> National Weather Service API

MCP client
  -> FastMCP tools
    -> Weather service functions
      -> National Weather Service API
```

## Requirements

- Python 3.13+
- uv
- Node.js 20+
- npm

## Backend

Install Python dependencies:

```bash
uv sync
```

Run the FastAPI server:

```bash
uv run uvicorn api:app --host 127.0.0.1 --port 8001
```

Run the MCP server over stdio:

```bash
uv run python weather.py
```

Run tests:

```bash
uv run python -m unittest
```

## Frontend

Install frontend dependencies:

```bash
cd frontend
npm install
```

Run the Nuxt dev server:

```bash
npm run dev -- --host 127.0.0.1 --port 3003
```

By default, the frontend calls `http://localhost:8001`. Override it with:

```bash
NUXT_PUBLIC_API_BASE=http://localhost:8001 npm run dev
```

## API

### `POST /forecast`

```json
{
  "latitude": 37.7749,
  "longitude": -122.4194
}
```

### `POST /alerts`

```json
{
  "state": "CA"
}
```

## Notes

The National Weather Service API primarily supports United States locations. Non-US coordinates may return a not-found response.
