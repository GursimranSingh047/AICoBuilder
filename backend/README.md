# ProjectPilot – Backend

> **AI Co-Builder** | FastAPI · PostgreSQL · Gemini · scikit-learn

---

## Architecture Overview

```
backend/
├── main.py                        # FastAPI app entry point
├── requirements.txt
├── Dockerfile
├── migrate.py                     # Dev migration helper
├── pytest.ini
│
├── app/
│   ├── core/
│   │   ├── config.py              # Pydantic-settings (reads .env)
│   │   ├── logging.py             # Loguru setup
│   │   └── security.py            # JWT + bcrypt helpers
│   │
│   ├── models/
│   │   ├── user.py                # SQLAlchemy User model
│   │   └── project.py             # Project + Prompt models
│   │
│   ├── schemas/
│   │   ├── user.py                # Pydantic request/response schemas
│   │   └── project.py             # Project/Chat/Suggest schemas
│   │
│   ├── routers/
│   │   ├── auth.py                # POST /auth/signup|login, GET /auth/me
│   │   ├── projects.py            # POST /projects/generate, GET/DELETE
│   │   ├── chat.py                # POST /chat/ /chat/improve /chat/explain
│   │   └── suggest.py             # POST /suggest/, GET /suggest/stacks
│   │
│   ├── services/
│   │   ├── gemini_service.py      # Gemini API wrapper (V2)
│   │   ├── ml_service.py          # scikit-learn classifier (V3)
│   │   └── project_generator.py   # Full generation pipeline (V1+V2)
│   │
│   ├── ml/
│   │   ├── train_model.py         # Standalone training script
│   │   └── project_type_model.pkl # Auto-generated on first run
│   │
│   ├── database.py                # SQLAlchemy engine + session
│   └── dependencies.py            # FastAPI dependency injection
│
└── tests/
    └── test_backend.py            # Full pytest test suite
```

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/signup` | Register new user | — |
| POST | `/auth/login` | Login, get JWT | — |
| GET | `/auth/me` | Current user profile | ✅ |
| POST | `/projects/generate` | Generate full project | Optional |
| GET | `/projects/` | List projects | Optional |
| GET | `/projects/{id}` | Project detail + files | — |
| GET | `/projects/{id}/download` | Download ZIP | — |
| DELETE | `/projects/{id}` | Delete project | Optional |
| POST | `/chat/` | Chat with AI assistant | — |
| POST | `/chat/improve` | Improve a code snippet | — |
| POST | `/chat/explain` | Explain a code snippet | — |
| POST | `/suggest/` | ML stack + feature suggestions | — |
| GET | `/suggest/stacks` | All available stacks | — |
| GET | `/suggest/features/{type}` | Features by project type | — |
| GET | `/health` | Health check | — |

---

## Quick Start (Local Dev)

### 1. Prerequisites
- Python 3.11+
- PostgreSQL (or use SQLite for dev – see `.env.example`)
- An OpenAI/Gemini API key (set `openai_api_key` in `.env`)

### 2. Clone & install

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env – add your openai_api_key and DATABASE_URL
```

### 4. Set up the database

```bash
# Create tables
python migrate.py

# (Optional) Pre-train the ML model
python -m app.ml.train_model
```

### 5. Start the server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit: **http://localhost:8000/docs** for the interactive Swagger UI.

---

## Quick Start (Docker)

```bash
# From the project root
cp backend/.env.example backend/.env   # Set openai_api_key

docker-compose up --build
```

- Backend: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

---

## Running Tests

```bash
cd backend
pytest -v
```

Tests use an in-memory SQLite database – no external services required.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `sqlite:///./projectpilot.db` | DB connection string |
| `SECRET_KEY` | Yes | `changeme` | JWT signing secret (32+ chars) |
| `openai_api_key` | Yes | — | OpenAI / Gemini API key (set in .env) |
| `OPENAI_MODEL` | No | `gemini-1.5-flash` | Model name (e.g. gemini-1.5-flash or gpt-3.5-turbo) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | JWT expiry |
| `PROJECTS_DIR` | No | `./generated_projects` | Where projects are saved |
| `ALLOWED_ORIGINS` | No | `localhost:3000,5173` | CORS origins (comma-separated) |
| `DEBUG` | No | `True` | Enables SQL query logging |

---

## AI & ML Layers

### V2 – Gemini Integration (`gemini_service.py`)
- `generate_project_code(idea, stack)` → dict of `{path: content}` files
- `generate_readme(idea, stack, name)` → Markdown string
- `chat(message, history, context)` → assistant reply
- `improve_code(code, instruction)` → refactored code
- `explain_code(code)` → plain-English explanation

Gracefully falls back to mock responses if the API key is absent.

### V3 – ML Personalisation (`ml_service.py`)
- TF-IDF + LinearSVC pipeline trained on 26 labelled project ideas
- Predicts one of 13 project types: `ecommerce`, `social`, `analytics`, `cms`, `saas`, `mobile`, `productivity`, `api`, `ml`, `game`, `fintech`, `healthcare`, `education`
- Returns recommended tech stack + top 6 suggested features + confidence score
- Model saved to `app/ml/project_type_model.pkl` and reloaded on startup

---

## Production Checklist

- [ ] Set a strong `SECRET_KEY` (32+ random chars)
- [ ] Set `DEBUG=false`
- [ ] Use PostgreSQL (`DATABASE_URL=postgresql://...`)
- [ ] Run Alembic migrations instead of `migrate.py`
- [ ] Put Uvicorn behind Nginx / a load balancer
- [ ] Restrict `ALLOWED_ORIGINS` to your frontend domain
- [ ] Store `openai_api_key` in a secrets manager (not in `.env`)
