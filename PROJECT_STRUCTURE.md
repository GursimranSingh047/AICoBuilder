# ProjectPilot - Project Structure

## Overview
ProjectPilot is a full-stack AI-powered project generator with a FastAPI backend and React frontend.

## Directory Structure

```
AICoBuilder/
├── .git/                           # Git repository
├── .kiro/                          # Kiro AI assistant specs
│   └── specs/
│       └── security-and-quality-fixes/
│           ├── .config.kiro
│           ├── bugfix.md
│           ├── design.md (future)
│           └── tasks.md (future)
├── .venv/                          # Python virtual environment (root level)
├── backend/                        # FastAPI backend application
│   ├── app/
│   │   ├── core/                   # Core configuration & utilities
│   │   │   ├── config.py           # Settings & environment config
│   │   │   ├── logging.py          # Loguru setup
│   │   │   └── security.py         # JWT & bcrypt helpers
│   │   ├── ml/                     # Machine learning models
│   │   │   ├── train_model.py      # ML training script
│   │   │   └── project_type_model.pkl  # Trained model
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   └── project.py
│   │   ├── routers/                # API endpoints
│   │   │   ├── auth.py             # Authentication routes
│   │   │   ├── projects.py         # Project generation routes
│   │   │   ├── chat.py             # AI chat routes
│   │   │   └── suggest.py          # ML suggestion routes
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   │   ├── user.py
│   │   │   └── project.py
│   │   ├── services/               # Business logic services
│   │   │   ├── gemini_service.py   # AI integration (OpenRouter/OpenAI/Gemini)
│   │   │   ├── ml_service.py       # ML predictions
│   │   │   └── project_generator.py # Project generation pipeline
│   │   ├── database.py             # Database connection & session
│   │   └── dependencies.py         # FastAPI dependency injection
│   ├── generated_projects/         # Generated project outputs (gitignored)
│   │   └── .gitkeep
│   ├── logs/                       # Application logs (gitignored)
│   ├── tests/                      # Backend tests
│   │   └── test_backend.py
│   ├── venv/                       # Backend virtual environment (gitignored)
│   ├── .env                        # Environment variables (gitignored)
│   ├── .env.example                # Environment template
│   ├── Dockerfile                  # Backend Docker configuration
│   ├── main.py                     # FastAPI application entry point
│   ├── migrate.py                  # Database migration helper
│   ├── pytest.ini                  # Pytest configuration
│   ├── README.md                   # Backend documentation
│   ├── requirements.txt            # Python dependencies
│   ├── projectpilot.db             # SQLite database (gitignored)
│   └── test.db                     # Test database (gitignored)
├── frontend/                       # React frontend application
│   ├── node_modules/               # NPM dependencies (gitignored)
│   ├── public/                     # Static assets
│   │   └── favicon.svg
│   ├── src/
│   │   ├── api/                    # API client
│   │   │   └── client.js           # Axios configuration & endpoints
│   │   ├── components/             # React components
│   │   │   ├── 3D/                 # 3D visualization components (new)
│   │   │   │   ├── CameraRig.jsx
│   │   │   │   ├── NetworkNodes.jsx
│   │   │   │   ├── DataFlow.jsx (planned)
│   │   │   │   ├── ScanEffect.jsx (planned)
│   │   │   │   └── CyberScene.jsx (planned)
│   │   │   ├── Layout/             # Layout components
│   │   │   │   ├── AppLayout.jsx
│   │   │   │   └── Sidebar.jsx
│   │   │   ├── UI/                 # Reusable UI components
│   │   │   │   └── index.jsx       # Spinner, ErrorBanner, etc.
│   │   │   ├── CodeViewer.jsx      # Syntax-highlighted code viewer
│   │   │   └── FileTree.jsx        # File tree explorer
│   │   ├── context/                # React context providers
│   │   │   └── AuthContext.jsx     # Authentication state
│   │   ├── pages/                  # Page components
│   │   │   ├── Chat.jsx            # AI chat interface
│   │   │   ├── Dashboard.jsx       # Main dashboard
│   │   │   ├── Generator.jsx       # Project generator
│   │   │   ├── Login.jsx           # Login page
│   │   │   ├── ProjectViewer.jsx   # Project file viewer
│   │   │   ├── Signup.jsx          # Signup page
│   │   │   └── Suggestions.jsx     # ML suggestions
│   │   ├── App.jsx                 # Main app component & routing
│   │   ├── index.css               # Global styles (Tailwind)
│   │   └── main.jsx                # React entry point
│   ├── index.html                  # HTML template
│   ├── package.json                # NPM dependencies & scripts
│   ├── package-lock.json           # NPM lock file
│   ├── postcss.config.js           # PostCSS configuration
│   ├── README.md                   # Frontend documentation
│   ├── tailwind.config.js          # Tailwind CSS configuration
│   └── vite.config.js              # Vite build configuration
├── .gitignore                      # Git ignore rules
├── docker-compose.yml              # Docker Compose configuration
├── PROJECT_STRUCTURE.md            # This file
└── README.md                       # Main project documentation
```

## Key Files & Their Purpose

### Backend
- **main.py**: FastAPI application entry point with CORS, error handling, and router registration
- **app/core/config.py**: Centralized configuration using Pydantic settings
- **app/services/gemini_service.py**: AI service supporting OpenRouter, OpenAI, and Gemini APIs
- **app/services/project_generator.py**: Core project generation logic combining ML + AI
- **app/routers/**: RESTful API endpoints organized by feature

### Frontend
- **src/api/client.js**: Axios client with interceptors for auth and error handling
- **src/pages/**: Main application pages (Generator, Chat, Dashboard, etc.)
- **src/components/**: Reusable React components
- **src/context/AuthContext.jsx**: Global authentication state management

## Environment Files

### Backend (.env)
```env
openai_api_key=your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
DATABASE_URL=sqlite:///./projectpilot.db
SECRET_KEY=your-secret-key
DEBUG=True
```

### Frontend
No .env file needed currently (API URL is hardcoded in client.js)

## Database
- **Development**: SQLite (projectpilot.db)
- **Production**: PostgreSQL (via docker-compose.yml)

## Generated Files (Gitignored)
- `backend/generated_projects/`: User-generated projects
- `backend/logs/`: Application logs
- `backend/__pycache__/`: Python bytecode
- `frontend/node_modules/`: NPM dependencies
- `*.db`: Database files
- `.venv/`, `venv/`: Virtual environments

## Development Workflow

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker
```bash
docker-compose up --build
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login and get JWT
- `GET /auth/me` - Get current user

### Projects
- `POST /projects/generate` - Generate new project
- `GET /projects/` - List projects
- `GET /projects/{id}` - Get project details
- `GET /projects/{id}/download` - Download project ZIP
- `DELETE /projects/{id}` - Delete project

### Chat
- `POST /chat/` - Send chat message
- `POST /chat/improve` - Improve code snippet
- `POST /chat/explain` - Explain code snippet

### Suggestions
- `POST /suggest/` - Get ML-based suggestions
- `GET /suggest/stacks` - Get available tech stacks
- `GET /suggest/features/{type}` - Get features by project type

## Tech Stack

### Backend
- **Framework**: FastAPI 0.111.0
- **Database**: SQLAlchemy 2.0.30 + SQLite/PostgreSQL
- **AI**: OpenRouter/OpenAI/Gemini API
- **ML**: scikit-learn 1.5.0
- **Auth**: python-jose + passlib
- **Logging**: loguru

### Frontend
- **Framework**: React 18.3.0
- **Build Tool**: Vite 5.3.0
- **Styling**: Tailwind CSS 3.4.4
- **Routing**: React Router 6.24.0
- **HTTP Client**: Axios 1.7.2
- **3D Graphics**: Three.js + @react-three/fiber + @react-three/drei
- **Code Highlighting**: react-syntax-highlighter

## Security Notes
- ⚠️ Never commit `.env` files
- ⚠️ Never commit API keys
- ⚠️ Never commit database files
- ⚠️ Review `.gitignore` before committing

## Maintenance
- Keep dependencies updated
- Run `npm audit` and `pip check` regularly
- Review logs periodically
- Clean up old generated projects
- Backup database before major changes
