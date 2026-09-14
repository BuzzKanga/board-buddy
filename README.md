# Board Buddy

A mini-kanban board application with a React frontend and FastAPI backend.

## Project Structure

```
board-buddy/
├── frontend/          # React + Vite SPA
├── backend/           # FastAPI REST API
├── docs/              # Project documentation
└── openapi.yaml       # API specification
```

## Prerequisites

- **Node.js** (v18+) and **npm** — for the frontend
- **Python** (3.11+) and [**uv**](https://docs.astral.sh/uv/) — for the backend

## Getting Started

### Backend

```bash
cd backend
uv sync                                      # Install dependencies
uv run uvicorn app.main:app --reload         # Start dev server on http://localhost:8000
```

- **API docs (Swagger UI):** http://localhost:8000/docs
- **Demo user:** `demo` / `password123`

To authenticate in Swagger UI, click the **Authorize** button and enter the demo credentials.

#### Running Tests

```bash
cd backend
uv run pytest -v
```

### Frontend

```bash
cd frontend
npm install                                  # Install dependencies
npm run dev                                  # Start dev server on http://localhost:5173
```

## API Authentication

All endpoints except `/auth/register` and `/auth/login` require a bearer token.

1. **Register** a new user:
   ```
   POST /auth/register
   Body: {"username": "yourname", "password": "yourpassword"}
   ```

2. **Login** to get a token:
   ```
   POST /auth/login
   Form data: username=demo, password=password123
   ```

3. **Use the token** in subsequent requests:
   ```
   Authorization: Bearer <your_access_token>
   ```

## Seed Data

The backend starts with demo data pre-loaded:

- **2 boards:** Product Launch, Bug Tracker
- **6 columns:** 3 per board (To Do, In Progress, Done)
- **8 cards:** distributed across columns with varying priorities and assignees
- **5 labels:** Feature, Design, Urgent, Bug, Backend

## Tech Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Frontend | React, Vite, TypeScript             |
| Backend  | FastAPI, Pydantic, Python           |
| Auth     | JWT (python-jose), bcrypt           |
| Storage  | In-memory (dictionaries)            |
