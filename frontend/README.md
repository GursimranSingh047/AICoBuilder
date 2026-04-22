# ProjectPilot — Frontend

> React + Vite + Tailwind CSS frontend for the AI Co-Builder platform.

---

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Start dev server (proxies API to http://127.0.0.1:8000)
npm run dev
```

Open **http://localhost:3000** in your browser.

> ⚠️ Make sure the backend is running first:
> ```bash
> cd ../backend && uvicorn main:app --reload
> ```

---

## Project Structure

```
src/
├── api/
│   └── client.js          ← All Axios API calls (exact backend endpoints)
├── context/
│   └── AuthContext.jsx    ← JWT auth state (login / signup / logout)
├── components/
│   ├── Layout/
│   │   ├── AppLayout.jsx  ← Sidebar + backend status bar
│   │   └── Sidebar.jsx    ← Navigation links + user section
│   ├── UI/
│   │   └── index.jsx      ← Spinner, PageLoader, ErrorBanner, StatCard…
│   ├── FileTree.jsx       ← Recursive file explorer for generated projects
│   └── CodeViewer.jsx     ← Syntax-highlighted code preview
├── pages/
│   ├── Dashboard.jsx      ← Stats + recent projects + quick actions
│   ├── Generator.jsx      ← Idea input → suggest → generate → file viewer
│   ├── Chat.jsx           ← Full conversational AI assistant (Gemini)
│   ├── Suggestions.jsx    ← ML stack + feature recommendations
│   ├── ProjectViewer.jsx  ← File tree + code viewer + AI explain
│   ├── Login.jsx
│   └── Signup.jsx
└── App.jsx                ← Router + providers
```

---

## API Mapping

All calls target `http://127.0.0.1:8000` (the FastAPI backend).

| Frontend action | Backend endpoint |
|----------------|-----------------|
| Generate project | `POST /projects/generate` |
| List projects | `GET /projects/` |
| Get project | `GET /projects/{id}` |
| Download ZIP | `GET /projects/{id}/download` |
| Delete project | `DELETE /projects/{id}` |
| Chat | `POST /chat/` |
| Explain code | `POST /chat/explain` |
| Improve code | `POST /chat/improve` |
| ML suggestion | `POST /suggest/` |
| All stacks | `GET /suggest/stacks` |
| Features by type | `GET /suggest/features/{type}` |
| Sign up | `POST /auth/signup` |
| Login | `POST /auth/login` |
| Me | `GET /auth/me` |

---

## Build for Production

```bash
npm run build        # outputs to dist/
npm run preview      # preview the production build locally
```
