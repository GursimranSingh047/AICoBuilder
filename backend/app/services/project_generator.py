"""
Project Generator Engine
Combines rule-based scaffolding (V1) with Gemini code generation (V2)
to produce a complete project on disk and as a downloadable ZIP.
"""

import io
import json
import os
import re
import zipfile
from pathlib import Path
from typing import Any

from loguru import logger

from app.core.config import settings
from app.services.gemini_service import gemini_service
from app.services.ml_service import ml_service, STACK_MAP

# ─── Boilerplate templates ────────────────────────────────────────────────────

BOILERPLATE: dict[str, dict[str, str]] = {
    "fastapi": {
        "main.py": '''\
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="{name}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {{"message": "Welcome to {name} API"}}
''',
        "requirements.txt": "fastapi\nuvicorn[standard]\npydantic\nsqlalchemy\n",
    },
    "react": {
        "src/App.jsx": '''\
import React from "react";

export default function App() {{
  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
      <h1 className="text-4xl font-bold">{name}</h1>
    </div>
  );
}}
''',
        "src/main.jsx": '''\
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
''',
        "src/index.css": "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n",
        "index.html": '''\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
''',
        "package.json": '''\
{{
  "name": "{slug}",
  "version": "1.0.0",
  "scripts": {{
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }},
  "dependencies": {{
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "axios": "^1.7.0"
  }},
  "devDependencies": {{
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }}
}}
''',
    },
    "nextjs": {
        "app/page.tsx": "export default function Home() {{ return <main><h1>{name}</h1></main>; }}\n",
        "package.json": '''\
{{
  "name": "{slug}",
  "version": "1.0.0",
  "scripts": {{"dev": "next dev", "build": "next build", "start": "next start"}},
  "dependencies": {{"next": "14.2.0", "react": "^18", "react-dom": "^18"}},
  "devDependencies": {{"typescript": "^5", "@types/react": "^18", "tailwindcss": "^3"}}
}}
''',
    },
}

FOLDER_STRUCTURE_MAP: dict[str, list[str]] = {
    "fastapi": ["app/", "app/models/", "app/routers/", "app/services/", "app/schemas/", "tests/"],
    "react":   ["src/", "src/components/", "src/pages/", "src/hooks/", "src/api/", "public/"],
    "nextjs":  ["app/", "components/", "lib/", "public/", "styles/"],
    "mobile":  ["src/", "src/screens/", "src/components/", "src/navigation/", "assets/"],
}


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9-]", "-", name.lower().strip()).strip("-")


class ProjectGeneratorService:
    """
    Orchestrates V1 (rule-based scaffolding) + V2 (Gemini code gen).
    """

    def generate(self, idea: str, project_name: str | None = None) -> dict[str, Any]:
        """
        Full pipeline: ML prediction → scaffold → Gemini code gen → disk write → zip.
        Returns a dict compatible with GenerateProjectResponse schema.
        """
        # ── Step 1: ML prediction ────────────────────────────────────────────
        prediction = ml_service.predict(idea)
        project_type = prediction["project_type"]
        stack = prediction["recommended_stack"]
        features = prediction["suggested_features"]

        logger.info(f"ML predicted type={project_type} confidence={prediction['confidence']}")

        # ── Step 2: Determine name / slug ────────────────────────────────────
        name = project_name or self._derive_name(idea)
        slug = _slugify(name)

        # ── Step 3: Rule-based scaffold ──────────────────────────────────────
        folder_structure = self._build_folder_structure(stack, project_type)
        files: dict[str, str] = self._generate_boilerplate(name, slug, stack)

        # ── Step 4: Gemini code generation ───────────────────────────────────
        try:
            ai_files = gemini_service.generate_project_code(idea, stack)
            if isinstance(ai_files, dict) and "raw" not in ai_files:
                files.update(ai_files)
                logger.info(f"Gemini generated {len(ai_files)} files.")
        except Exception as exc:
            logger.warning(f"Gemini code generation skipped: {exc}")

        # ── Step 5: README ───────────────────────────────────────────────────
        readme = gemini_service.generate_readme(idea, stack, name)
        files["README.md"] = readme

        # ── Step 6: Write to disk ────────────────────────────────────────────
        local_path = self._write_to_disk(slug, files)

        # ── Step 7: Create ZIP ───────────────────────────────────────────────
        zip_path = self._create_zip(slug, files)

        return {
            "name": name,
            "tech_stack": {**stack, "project_type": project_type},
            "folder_structure": folder_structure,
            "files": files,
            "readme": readme,
            "local_path": str(local_path),
            "zip_path": str(zip_path),
            "suggested_features": features,
        }

    # ─── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _derive_name(idea: str) -> str:
        words = idea.strip().split()[:3]
        return " ".join(w.capitalize() for w in words) + " App"

    @staticmethod
    def _build_folder_structure(stack: dict[str, str], project_type: str) -> dict[str, Any]:
        frontend = stack.get("frontend", "React").lower()
        backend = stack.get("backend", "FastAPI").lower()

        fe_key = "nextjs" if "next" in frontend else ("mobile" if "native" in frontend else "react")
        be_key = "fastapi" if "fastapi" in backend else "fastapi"

        return {
            "frontend": FOLDER_STRUCTURE_MAP.get(fe_key, FOLDER_STRUCTURE_MAP["react"]),
            "backend": FOLDER_STRUCTURE_MAP.get(be_key, FOLDER_STRUCTURE_MAP["fastapi"]),
        }

    @staticmethod
    def _generate_boilerplate(name: str, slug: str, stack: dict[str, str]) -> dict[str, str]:
        files: dict[str, str] = {}
        frontend = stack.get("frontend", "").lower()
        backend = stack.get("backend", "").lower()

        fe_key = "nextjs" if "next" in frontend else "react"
        be_key = "fastapi" if "fastapi" in backend else "fastapi"

        for template_key in [fe_key, be_key]:
            templates = BOILERPLATE.get(template_key, {})
            for path, content in templates.items():
                try:
                    files[path] = content.format(name=name, slug=slug)
                except KeyError:
                    files[path] = content

        # .env template
        files[".env.example"] = (
          f"# {name} Environment Variables\n"
          "DATABASE_URL=postgresql://user:pass@localhost:5432/db\n"
          "SECRET_KEY=changeme\n"
          "openai_api_key=your-key\n"
        )

        # docker-compose
        files["docker-compose.yml"] = f"""\
version: "3.9"
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: {slug}
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports: ["5432:5432"]
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [db]
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
"""
        return files

    def _write_to_disk(self, slug: str, files: dict[str, str]) -> Path:
        project_dir = settings.projects_path / slug
        for rel_path, content in files.items():
            full_path = project_dir / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
        logger.info(f"Project written to {project_dir}")
        return project_dir

    def _create_zip(self, slug: str, files: dict[str, str]) -> Path:
        zip_path = settings.projects_path / f"{slug}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for rel_path, content in files.items():
                zf.writestr(f"{slug}/{rel_path}", content)
        logger.info(f"ZIP created: {zip_path}")
        return zip_path


# Singleton
project_generator = ProjectGeneratorService()
