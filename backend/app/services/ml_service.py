"""
ML Service – lightweight scikit-learn text classifier that predicts project type,
recommended tech stack, and suggested features from a plain-text idea.

Training runs once on startup if no saved model is found.
"""

import json
from pathlib import Path
from typing import Any, Optional, List, Dict, Tuple

import joblib
import numpy as np
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

# ─── Training Data ────────────────────────────────────────────────────────────

TRAINING_DATA: List[Tuple[str, str]] = [
    # (idea snippet, project_type)
    ("ecommerce shop online store cart payment stripe", "ecommerce"),
    ("buy sell product catalog checkout order", "ecommerce"),
    ("marketplace selling listing invoice", "ecommerce"),
    ("social media posts feed likes followers profile", "social"),
    ("chat messaging real-time websocket friends", "social"),
    ("community forum discussion threads comments", "social"),
    ("dashboard analytics charts graphs metrics kpi", "analytics"),
    ("reporting data visualization business intelligence", "analytics"),
    ("monitoring logs metrics prometheus grafana", "analytics"),
    ("blog cms content articles markdown editor", "cms"),
    ("portfolio website landing page personal site", "cms"),
    ("documentation wiki knowledge base articles", "cms"),
    ("saas subscription users billing tenant", "saas"),
    ("multi tenant plans pricing upgrade admin", "saas"),
    ("crm customers leads sales pipeline", "saas"),
    ("mobile app ios android react native flutter", "mobile"),
    ("todo task manager productivity reminder", "productivity"),
    ("calendar schedule event booking appointment", "productivity"),
    ("note taking writing organization", "productivity"),
    ("api rest graphql microservice backend service", "api"),
    ("machine learning model training dataset prediction", "ml"),
    ("ai chatbot nlp recommendation neural network", "ml"),
    ("game 2d 3d unity canvas player score", "game"),
    ("fintech banking payment wallet transaction ledger", "fintech"),
    ("healthcare medical patient appointment doctor", "healthcare"),
    ("education learning quiz course lesson student", "education"),
]

STACK_MAP: Dict[str, Dict[str, str]] = {
    "ecommerce":   {"frontend": "Next.js", "backend": "FastAPI", "database": "PostgreSQL", "extra": "Stripe, Redis"},
    "social":      {"frontend": "React",   "backend": "FastAPI", "database": "PostgreSQL", "extra": "WebSocket, Redis"},
    "analytics":   {"frontend": "React",   "backend": "FastAPI", "database": "ClickHouse", "extra": "Pandas, Plotly"},
    "cms":         {"frontend": "Next.js", "backend": "FastAPI", "database": "PostgreSQL", "extra": "S3, Markdown"},
    "saas":        {"frontend": "React",   "backend": "FastAPI", "database": "PostgreSQL", "extra": "Stripe, Redis, Celery"},
    "mobile":      {"frontend": "React Native", "backend": "FastAPI", "database": "SQLite/PostgreSQL", "extra": "Expo"},
    "productivity":{"frontend": "React",   "backend": "FastAPI", "database": "SQLite",     "extra": "PWA"},
    "api":         {"frontend": "N/A",     "backend": "FastAPI", "database": "PostgreSQL", "extra": "Redis, Docker"},
    "ml":          {"frontend": "Streamlit/React", "backend": "FastAPI", "database": "PostgreSQL", "extra": "scikit-learn, PyTorch"},
    "game":        {"frontend": "Phaser.js/Unity", "backend": "FastAPI", "database": "Redis",      "extra": "WebSocket"},
    "fintech":     {"frontend": "React",   "backend": "FastAPI", "database": "PostgreSQL", "extra": "Stripe, Celery"},
    "healthcare":  {"frontend": "React",   "backend": "FastAPI", "database": "PostgreSQL", "extra": "HL7/FHIR"},
    "education":   {"frontend": "Next.js", "backend": "FastAPI", "database": "PostgreSQL", "extra": "S3, Celery"},
}

FEATURES_MAP: Dict[str, List[str]] = {
    "ecommerce":   ["Product catalog", "Shopping cart", "Checkout flow", "Order tracking", "Payment integration", "Inventory management"],
    "social":      ["User profiles", "News feed", "Real-time messaging", "Follow/friend system", "Notifications", "Media uploads"],
    "analytics":   ["Interactive dashboards", "Custom date ranges", "CSV/Excel export", "User segmentation", "Alerts", "API data ingestion"],
    "cms":         ["Rich text editor", "Media library", "Tag/category system", "SEO tools", "Draft/publish workflow", "Version history"],
    "saas":        ["Multi-tenancy", "Subscription billing", "Role-based access", "Audit logs", "API key management", "Usage metering"],
    "mobile":      ["Push notifications", "Offline mode", "Biometric auth", "Deep links", "Camera/gallery access", "App store deploy"],
    "productivity":["Task CRUD", "Due dates & reminders", "Drag-and-drop", "Labels/tags", "Team sharing", "Calendar sync"],
    "api":         ["RESTful endpoints", "JWT auth", "Rate limiting", "OpenAPI docs", "Versioning", "Webhook support"],
    "ml":          ["Model training pipeline", "Prediction API", "Feature engineering", "Model versioning", "Experiment tracking", "Data visualization"],
    "game":        ["Player auth", "Leaderboard", "Game state persistence", "Real-time multiplayer", "In-game shop", "Analytics"],
    "fintech":     ["Transactions ledger", "KYC flow", "Multi-currency", "Fraud detection", "Reporting", "Audit trail"],
    "healthcare":  ["Patient records", "Appointment booking", "Prescription management", "Billing", "Role-based access", "Audit logs"],
    "education":   ["Course builder", "Quizzes", "Progress tracking", "Video hosting", "Certificates", "Discussion boards"],
}

MODEL_PATH = Path(__file__).parent / "../ml/project_type_model.pkl"


class MLService:
    def __init__(self):
        self._pipeline: Optional[Pipeline] = None
        self._classes: List[str] = []
        self._load_or_train()

    # ─── Model lifecycle ──────────────────────────────────────────────────────

    def _train(self) -> None:
        texts, labels = zip(*TRAINING_DATA)
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000, sublinear_tf=True)),
            ("clf",   OneVsRestClassifier(LinearSVC(max_iter=2000))),
        ])
        pipeline.fit(list(texts), list(labels))
        self._pipeline = pipeline
        self._classes = list(pipeline.classes_)
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"pipeline": pipeline, "classes": self._classes}, MODEL_PATH)
        logger.info(f"ML model trained and saved → {MODEL_PATH}")

    def _load_or_train(self) -> None:
        if MODEL_PATH.exists():
            try:
                data = joblib.load(MODEL_PATH)
                self._pipeline = data["pipeline"]
                self._classes = data["classes"]
                logger.info(f"ML model loaded from {MODEL_PATH}")
                return
            except Exception as exc:
                logger.warning(f"Could not load model ({exc}); retraining.")
        self._train()

    # ─── Prediction ───────────────────────────────────────────────────────────

    def predict(self, idea: str) -> Dict[str, Any]:
        """
        Given a plain-text project idea, return:
        - project_type
        - recommended_stack
        - suggested_features
        - confidence (0-1)
        """
        if self._pipeline is None:
            return self._fallback(idea)

        try:
            # Decision function → confidence scores
            scores: np.ndarray = self._pipeline.decision_function([idea])[0]

            # Normalise scores to [0, 1] range for readability
            scores_min, scores_max = scores.min(), scores.max()
            if scores_max > scores_min:
                norm_scores = (scores - scores_min) / (scores_max - scores_min)
            else:
                norm_scores = np.ones_like(scores) / len(scores)

            best_idx = int(np.argmax(norm_scores))
            project_type = self._classes[best_idx]
            confidence = float(round(norm_scores[best_idx], 4))

            return {
                "project_type": project_type,
                "recommended_stack": STACK_MAP.get(project_type, STACK_MAP["api"]),
                "suggested_features": FEATURES_MAP.get(project_type, [])[:6],
                "confidence": confidence,
                "all_scores": {
                    cls: float(round(score, 4))
                    for cls, score in zip(self._classes, norm_scores)
                },
            }
        except Exception as exc:
            logger.error(f"ML prediction error: {exc}")
            return self._fallback(idea)

    @staticmethod
    def _fallback(idea: str) -> Dict[str, Any]:
        """Safe default when the model is unavailable."""
        return {
            "project_type": "saas",
            "recommended_stack": STACK_MAP["saas"],
            "suggested_features": FEATURES_MAP["saas"],
            "confidence": 0.0,
            "all_scores": {},
        }


# Singleton instance
ml_service = MLService()
