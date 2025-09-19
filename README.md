## AI Org Dashboard

An end-to-end metrics dashboard for AI tools. It ingests usage data from external providers, stores it in Postgres, exposes normalized/aggregated APIs via FastAPI, and renders an interactive React dashboard.

### Architecture Overview

- **Orchestration (docker-compose)**
  - Services: `postgres`, `api` (FastAPI), `collector` (ingestion worker), `dashboard` (React served by Nginx).
  - Internal networking between services; the dashboard calls the API via `VITE_API_URL`.

- **Data Flow**
  - Collector fetches metrics from external systems (OpenAI, Copilot, Claude, Cursor) and writes to Postgres.
  - API reads, normalizes, and aggregates metrics from Postgres.
  - Dashboard queries the API to render charts, tables, and KPIs with filtering and auth.

- **Components**
  - Postgres: persistent store, initialized by `infra/init-db.sql`.
  - API (`api/`): FastAPI app with metrics router, health, and demo auth.
  - Collector (`collector/`): CLI/daemon orchestrating per-provider collectors.
  - Dashboard (`dashboard/`): React + TypeScript, built and served by Nginx.

### Design Patterns

- **Layered architecture**: Ingestion → Persistence → Service → Presentation.
- **Router/Controller (API)**: `api/app.py` wires the app; `api/metrics.py` defines endpoints; `api/db.py` is the data-access layer.
- **DAO/Repository-lite**: Centralized DB connection and DTO mapping in `api/db.py` (`format_metrics`, `get_dashboard_stats`).
- **Adapter (Collectors)**: Each provider module (`collector/openai.py`, `collector/copilot.py`, `collector/claude.py`, `collector/cursor.py`) adapts external APIs into a common schema. `collector/collector.py` orchestrates uniformly.

- **Facade/Aggregator**: `get_dashboard_stats()` composes cross-table stats into a single response tailored for the UI.

- **Service object (Frontend)**: `dashboard/src/services/apiService.ts` encapsulates HTTP, timeouts, retries/backoff, and auth headers.

- **Context + Reducer (Auth)**: `dashboard/src/contexts/AuthContext.tsx` manages user/token and integrates with API auth endpoints.

- **Stateless API + token auth (demo)**: Simple token validation via `/auth/*` endpoints (mock JWT-like tokens for development).

### Key Paths

- Compose: `docker-compose.yml`
- Infra SQL: `infra/init-db.sql`
- API: `api/app.py`, `api/metrics.py`, `api/db.py`
- Collector: `collector/collector.py` and provider files
- Dashboard: `dashboard/src/*`

### API Surface (selected)

- `GET /` — health ping
- `GET /health` — DB connectivity and table summaries
- `POST /auth/login` — returns `{ user, token }` for demo creds (`admin`/`admin123`)
- `GET /auth/validate`, `POST /auth/refresh`
- `GET /metrics/stats` — aggregated KPIs
- `GET /metrics/openai|claude|copilot|cursor` — list metrics with `start_date`, `end_date`, `sort_by`, `sort_order`

### Dashboard Data Contracts (DTO excerpt)

```json
{
  "id": "string",
  "applicationId": "chatgpt|claude|copilot|cursor",
  "timestamp": "ISO-8601",
  "responseTime": 0,
  "requestCount": 0,
  "errorRate": 0,
  "successRate": 100,
  "averageTokens": 0,
  "cost": 0,
  "uptime": 100
}
```

### Running Locally

1. Create a `.env` in repo root (if provider collectors need secrets).
2. Start everything:

```bash
docker compose up --build
```

3. Access:
   - API: `http://localhost:5000`
   - Dashboard: `http://localhost:3000`

4. Demo login:

```text
username: admin
password: admin123
```

### Configuration

- API env (see `docker-compose.yml`): `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `CORS_ORIGINS`, `PORT`, `HOST`.
- Dashboard env: `VITE_API_URL` (in compose set to `http://localhost:5000`).
- Collector: provider-specific env via `.env` and files under `collector/`.

### Operational Notes

- Resilience: API returns structured errors; frontend retries with exponential backoff and timeout; collector logs per-source failures, continues others.
- Scalability: independent services; restrict payload sizes via SQL filters/limits; collectors can run on intervals (`--interval`) or once (`--once`).
- Observability: `GET /health`, DB verification, collector logs (`logs/`, stdout).

### Development

- Backend: FastAPI + psycopg2. Run via compose or `uvicorn app:app --reload` in `api/` with proper env.
- Frontend: Vite + React + MUI. In `dashboard/` use `npm install && npm run dev` (when not using Docker) and set `VITE_API_URL`.
- Collector: Run `python collector.py --once` in `collector/` with `.env` configured.

### Security

This repo uses demo authentication suitable only for development. Replace with real identity provider/JWT validation and tighten CORS before production.


