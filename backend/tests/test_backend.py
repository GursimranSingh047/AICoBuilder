"""
Test suite for ProjectPilot backend.

Run with:
    pytest -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.services.ml_service import ml_service
from main import app

# ─── Test DB (SQLite in-memory) ───────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite:///./test_projectpilot.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    """Register a test user and return credentials + token."""
    payload = {"email": "test@example.com", "username": "testuser", "password": "securepass123"}
    resp = client.post("/auth/signup", json=payload)
    # If already registered, log in instead
    if resp.status_code == 400:
        resp = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    data = resp.json()
    return {"token": data["access_token"], **payload}


# ─── Security tests ───────────────────────────────────────────────────────────

class TestSecurity:
    def test_password_hash_and_verify(self):
        hashed = hash_password("mysecret")
        assert verify_password("mysecret", hashed)
        assert not verify_password("wrongpass", hashed)

    def test_jwt_encode_decode(self):
        token = create_access_token({"sub": "42"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "42"

    def test_invalid_jwt(self):
        assert decode_access_token("notavalidtoken") is None


# ─── Auth endpoint tests ──────────────────────────────────────────────────────

class TestAuth:
    def test_signup(self, client):
        resp = client.post("/auth/signup", json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "strongpass99",
        })
        assert resp.status_code in (201, 400)  # 400 if already exists in session

    def test_login_success(self, client, registered_user):
        resp = client.post("/auth/login", json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, registered_user):
        resp = client.post("/auth/login", json={
            "email": registered_user["email"],
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    def test_me_authenticated(self, client, registered_user):
        resp = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        assert resp.status_code == 200
        assert resp.json()["email"] == registered_user["email"]

    def test_me_unauthenticated(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401


# ─── Suggest / ML tests ───────────────────────────────────────────────────────

class TestSuggest:
    def test_suggest_ecommerce(self, client):
        resp = client.post("/suggest/", json={"idea": "An online shop with cart and checkout"})
        assert resp.status_code == 200
        data = resp.json()
        assert "recommended_stack" in data
        assert "suggested_features" in data
        assert 0.0 <= data["confidence"] <= 1.0

    def test_suggest_ml_project(self, client):
        resp = client.post("/suggest/", json={"idea": "A machine learning model for image classification with training pipeline"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["project_type"] in ["ml", "analytics", "api", "saas"]  # flexible

    def test_list_stacks(self, client):
        resp = client.get("/suggest/stacks")
        assert resp.status_code == 200
        assert "ecommerce" in resp.json()

    def test_features_for_type(self, client):
        resp = client.get("/suggest/features/social")
        assert resp.status_code == 200
        data = resp.json()
        assert data["project_type"] == "social"
        assert len(data["features"]) > 0

    def test_ml_predict_directly(self):
        result = ml_service.predict("A real-time chat app with rooms and messages")
        assert "project_type" in result
        assert "recommended_stack" in result
        assert isinstance(result["suggested_features"], list)


# ─── Project generation tests ─────────────────────────────────────────────────

class TestProjects:
    def test_generate_project(self, client):
        resp = client.post("/projects/generate", json={
            "idea": "A simple todo list app with user auth and real-time sync",
            "project_name": "TodoApp",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "TodoApp"
        assert "files" in data
        assert "README.md" in data["files"]
        assert data["status"] == "completed"
        return data["project_id"]

    def test_list_projects(self, client):
        resp = client.get("/projects/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_project(self, client):
        # First create one
        create_resp = client.post("/projects/generate", json={
            "idea": "A blog platform with markdown support",
            "project_name": "BlogPilot",
        })
        pid = create_resp.json()["project_id"]

        resp = client.get(f"/projects/{pid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == pid

    def test_get_nonexistent_project(self, client):
        resp = client.get("/projects/99999")
        assert resp.status_code == 404


# ─── Chat tests ───────────────────────────────────────────────────────────────

class TestChat:
    def test_chat_basic(self, client):
        resp = client.post("/chat/", json={
            "message": "What tech stack should I use for a real-time app?",
            "history": [],
        })
        assert resp.status_code == 200
        assert "reply" in resp.json()

    def test_chat_with_history(self, client):
        resp = client.post("/chat/", json={
            "message": "Can you elaborate on the database choice?",
            "history": [
                {"role": "user", "content": "What stack for ecommerce?"},
                {"role": "assistant", "content": "I recommend Next.js + FastAPI + PostgreSQL."},
            ],
        })
        assert resp.status_code == 200

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
