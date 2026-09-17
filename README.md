# Board Buddy

A modern mini-kanban board application featuring a **React (TanStack Start)** frontend and a **FastAPI** backend with real-time ready architecture.

---

## Features

- **Multi-Board Management:** Create, view, rename, and delete boards with custom configurations.
- **Kanban Columns:** Flexible columns per board (e.g., *To Do*, *In Progress*, *Done*) with reordering and column deletion protection.
- **Card Workflows:** Full card lifecycle management with title, markdown-ready description, assignees, due dates, and priority levels (*Low*, *Medium*, *High*).
- **Board-Scoped Labels:** Create colored labels and tag/untag cards with multiple labels.
- **Connected Architecture:** Single-page frontend wired directly to the FastAPI REST backend.
- **Interactive API Documentation:** Automatically generated OpenAPI/Swagger UI and ReDoc interfaces.
- **Instant Demo Seed Data:** Pre-loaded with realistic boards, columns, cards, and labels on startup.

---

## Project Structure

```
board-buddy/
├── frontend/                  # React + TanStack Start frontend
│   ├── src/
│   │   ├── components/kanban/ # Kanban board, cards, avatars, and dialogs
│   │   ├── components/ui/     # Radix UI primitives and styled components
│   │   ├── routes/            # File-based routes (/, /boards/$boardId)
│   │   └── services/          # REST API client (api.ts) & type definitions
│   └── package.json
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── routers/           # Endpoint handlers (auth, boards, columns, cards, labels)
│   │   ├── models.py          # Pydantic v2 schemas and validation
│   │   ├── store.py           # In-memory data store with initial seed data
│   │   └── main.py            # FastAPI app initialization & CORS middleware
│   ├── tests/                 # Comprehensive pytest test suite
│   └── pyproject.toml         # Python dependencies managed via uv
├── docs/                      # Technical specifications and documentation
│   └── spec.md
└── openapi.yaml               # OpenAPI 3.1 specification
```

---

## Prerequisites

- **Node.js** (v18+) and **npm** — for the frontend
- **Python** (3.11+) and [**uv**](https://docs.astral.sh/uv/) — for the backend

---

## Getting Started

### Run with Docker

The easiest way to run Board Buddy is using Docker. This will build and run both the frontend and backend in a single container.

```bash
# Build the Docker image
docker build -t board-buddy .

# Run the container
docker run -p 8000:8000 board-buddy
```

The application will be available at [http://localhost:8000](http://localhost:8000).

### Manual Setup

To run the full stack locally without Docker, open two terminal windows (one for the backend and one for the frontend).

### 1. Start the Backend

```bash
cd backend
uv sync                                      # Install dependencies
uv run uvicorn app.main:app --reload         # Start dev server on http://localhost:8000
```

- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

#### Database Configuration

The backend uses SQLAlchemy and is database-agnostic. Configure the connection via the `DATABASE_URL` environment variable:

- **Default (SQLite):** `sqlite:///./board_buddy.db`
- **PostgreSQL:** `postgresql+psycopg2://boardbuddy:boardbuddy@localhost:5432/board_buddy`

To quickly start a local PostgreSQL database for development, you can run this Docker command:

```bash
docker run -d \
  --name board-buddy-db \
  -e POSTGRES_USER=boardbuddy \
  -e POSTGRES_PASSWORD=boardbuddy \
  -e POSTGRES_DB=board_buddy \
  -p 5432:5432 \
  -v board-buddy-pgdata:/var/lib/postgresql/data \
  postgres:16-alpine
```

> [!NOTE]
> **Authentication Status:** Authentication is currently bypassed for rapid local development. All endpoints are open and associate actions with an anonymous user context (`get_current_user()` returns `"anonymous"`). JWT authentication will be restored in a future milestone.

### 2. Start the Frontend

```bash
cd frontend
npm install                                  # Install dependencies
npm run dev                                  # Start dev server on http://localhost:5173
```

- **Frontend Application:** [http://localhost:5173](http://localhost:5173)

The frontend automatically communicates with the backend at `http://localhost:8000`.

---

## Testing & Quality Checks

### Backend Tests

The backend includes a comprehensive suite of unit and integration tests using `pytest` and HTTPX TestClient:

```bash
cd backend
uv run pytest -v
```

### Frontend Checks

```bash
cd frontend
npm run build                                # Build production bundle with Vite/Nitro
npm run lint                                 # Lint codebase using ESLint
npm run format                               # Check / format code with Prettier
```

---

## Seed Data

On initial startup, the backend automatically creates database tables and seeds demo data if the database is empty:

- **2 Boards:**
  - *Product Launch*
  - *Bug Tracker*
- **6 Columns:** 3 per board (*To Do*, *In Progress*, *Done*)
- **8 Cards:** Distributed across columns with diverse priorities, assignees, and due dates
- **5 Labels:** *Feature*, *Design*, *Urgent*, *Bug*, *Backend*

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/boards` | List all boards |
| `POST` | `/boards` | Create a board (auto-creates 3 default columns) |
| `GET` | `/boards/{boardId}` | Get full board details (columns, cards, labels) |
| `PATCH` | `/boards/{boardId}` | Update board title |
| `DELETE` | `/boards/{boardId}` | Delete a board and all associated resources |
| `POST` | `/boards/{boardId}/columns` | Create a new column on a board |
| `PATCH` | `/columns/{columnId}` | Update column name or position order |
| `DELETE` | `/columns/{columnId}` | Delete a column and its cards |
| `POST` | `/columns/{columnId}/cards` | Create a card in a column |
| `PATCH` | `/cards/{cardId}` | Update card details, column, or order position |
| `DELETE` | `/cards/{cardId}` | Delete a card |
| `GET` | `/boards/{boardId}/labels` | List labels belonging to a board |
| `POST` | `/boards/{boardId}/labels` | Create a new label on a board |
| `DELETE` | `/labels/{labelId}` | Delete a label |
| `POST` | `/cards/{cardId}/labels/{labelId}` | Attach a label to a card |
| `DELETE` | `/cards/{cardId}/labels/{labelId}` | Detach a label from a card |
| `POST` | `/auth/token` | OAuth2 form login (stub) |
| `GET` | `/auth/me` | Current user profile |

Full endpoint schemas and request/response models are viewable in the Swagger UI (`/docs`) or in [openapi.yaml](openapi.yaml).

---

## Tech Stack

| Layer | Technology | Description |
|---|---|---|
| **Frontend Framework** | [React 19](https://react.dev/) + [TanStack Start](https://tanstack.com/start) | SSR-ready React application with file-based routing |
| **Frontend State & Routing** | [TanStack Router](https://tanstack.com/router) & [TanStack Query](https://tanstack.com/query) | Robust routing and client-side data fetching |
| **Styling & UI** | [Tailwind CSS v4](https://tailwindcss.com/) + [Radix UI](https://www.radix-ui.com/) | Accessible component primitives and utility styling |
| **Icons** | [Lucide React](https://lucide.dev/) | Modern UI icons |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance Python async web framework |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) | Strict data schemas and validation |
| **Python Tooling** | [uv](https://docs.astral.sh/uv/) | Fast Python package management and virtual environments |
| **Testing** | [pytest](https://pytest.org/) & HTTPX | Automated test runner and HTTP client |
| **Storage** | In-memory store | Ephemeral data store initialized on startup |
| **API Contract** | OpenAPI 3.1 | Standardized REST API specification |
