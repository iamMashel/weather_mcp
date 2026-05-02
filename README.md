# Weather MCP

[![CI](https://github.com/iamMashel/weather_mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/iamMashel/weather_mcp/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-REST-009688?logo=fastapi&logoColor=white)
![Nuxt](https://img.shields.io/badge/Nuxt-4-00DC82?logo=nuxt&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-enabled-111827)

An MCP-powered full-stack weather application that exposes National Weather Service data through an MCP server, a FastAPI bridge, and a Nuxt dashboard.

## Why It Matters

Weather MCP demonstrates a clean pattern for building AI-tooling projects that are also useful as normal web apps. The core weather service is shared by both the MCP tools and the REST API, so the system avoids duplicate business logic while supporting agent clients and browser users.

## Features

- MCP tools for active alerts and short-range forecasts
- FastAPI endpoints for browser and frontend clients
- Structured JSON responses for forecasts and alerts
- Nuxt UI with forecast cards, alert severity styling, loading states, and validation
- Backend tests that mock upstream weather calls

## Tech Stack

| Layer | Tools |
| --- | --- |
| MCP server | FastMCP, Python |
| API | FastAPI, Pydantic, httpx |
| Frontend | Nuxt 4, Vue 3 |
| Package management | uv, npm |
| Quality | unittest, GitHub Actions |

## Architecture

```mermaid
flowchart LR
    user[Browser User] --> ui[Nuxt Frontend]
    ui --> api[FastAPI REST API]
    api --> service[Weather Service Layer]
    service --> nws[National Weather Service API]

    mcp_client[MCP Client] --> mcp[FastMCP Server]
    mcp --> service

    subgraph frontend[Frontend]
        ui
    end

    subgraph backend[Backend]
        api
        mcp
        service
    end

    subgraph external[External Data]
        nws
    end
```

The app has two entry points over one shared weather service layer. Browser users call the FastAPI bridge through the Nuxt dashboard, while MCP clients call the FastMCP tools directly. Both paths reuse the same National Weather Service integration.

## Request Flow

```mermaid
sequenceDiagram
    participant User
    participant Nuxt as Nuxt frontend
    participant API as FastAPI
    participant Weather as Weather service
    participant NWS as National Weather Service

    User->>Nuxt: Submit coordinates or state code
    Nuxt->>API: POST /forecast or /alerts
    API->>API: Validate request with Pydantic
    API->>Weather: Fetch structured weather data
    Weather->>NWS: Request points, forecast, or alerts
    NWS-->>Weather: GeoJSON response
    Weather-->>API: Normalized forecast or alert objects
    API-->>Nuxt: JSON response
    Nuxt-->>User: Render cards, badges, and messages
```

## Backend Design

```mermaid
flowchart TB
    api["api.py<br/>FastAPI app<br/>Forecast endpoint<br/>Alerts endpoint<br/>Pydantic validation<br/>HTTP error mapping"]
    weather["weather.py<br/>fetch_forecast()<br/>fetch_alerts()<br/>get_forecast()<br/>get_alerts()<br/>create_mcp_server()"]
    nws["National Weather Service<br/>points endpoint<br/>forecast endpoint<br/>active alerts endpoint"]

    api -->|imports service functions| weather
    weather -->|httpx requests| nws
```

`weather.py` keeps MCP registration lazy so importing the service from FastAPI does not start MCP machinery. REST endpoints return structured JSON, while MCP tools format the same data as readable text.

## Frontend Design

```mermaid
flowchart TD
    page[index.vue] --> forecast_form[Forecast form]
    page --> alerts_form[Alerts form]
    forecast_form --> forecast_state[Loading, error, and period state]
    alerts_form --> alerts_state[Loading, error, empty, and alert state]
    forecast_state --> forecast_cards[Forecast cards]
    alerts_state --> alert_cards[Severity-coded alert cards]
    config[Nuxt runtime config] --> page
```

The Nuxt page consumes API objects directly instead of parsing display text. Runtime config controls the backend URL through `NUXT_PUBLIC_API_BASE`, which keeps local development and deployment settings separate from the component code.

## Requirements

- Python 3.13+
- uv
- Node.js 20+
- npm

## Quickstart

Run the backend:

```bash
uv sync
uv run uvicorn api:app --host 127.0.0.1 --port 8001
```

Run the frontend:

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 3003
```

Open `http://127.0.0.1:3003`.

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
uv run python -m unittest discover -s tests -v
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

Example response:

```json
{
  "data": [
    {
      "name": "Tonight",
      "temperature": 56,
      "temperatureUnit": "F",
      "windSpeed": "8 mph",
      "windDirection": "W",
      "shortForecast": "Mostly Clear",
      "detailedForecast": "Mostly clear, with a low around 56.",
      "icon": "https://api.weather.gov/icons/land/night/skc",
      "isDaytime": false
    }
  ]
}
```

### `POST /alerts`

```json
{
  "state": "CA"
}
```

## Quality Checks

```bash
uv run python -m unittest discover -s tests -v
cd frontend && npm run build
```

## Roadmap

- City search with geocoding
- Hourly forecast endpoint
- Temperature and wind charts
- Alert map with affected zones
- Response caching for NWS calls
- Deployment guide for a public demo

## Contributing

Contributions are welcome. Please open an issue first for larger changes so the design can stay focused.

## Notes

The National Weather Service API primarily supports United States locations. Non-US coordinates may return a not-found response.
