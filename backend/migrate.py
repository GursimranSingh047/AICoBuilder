"""
migrate.py – Lightweight migration helper for development.

Usage:
    python migrate.py         # Create / update all tables
    python migrate.py drop    # Drop all tables (DESTRUCTIVE – dev only)
    python migrate.py reset   # Drop + recreate all tables

For production, use Alembic:
    alembic init alembic
    alembic revision --autogenerate -m "initial"
    alembic upgrade head
"""

import sys
from loguru import logger
from app.database import engine, Base
from app.models import user, project  # noqa – side-effect imports


def create_all():
    Base.metadata.create_all(bind=engine)
    logger.info("✅ All tables created / verified.")


def drop_all():
    confirm = input("⚠️  Drop ALL tables? This is irreversible. Type 'yes' to confirm: ")
    if confirm.strip().lower() == "yes":
        Base.metadata.drop_all(bind=engine)
        logger.info("🗑️  All tables dropped.")
    else:
        logger.info("Aborted.")


def reset():
    drop_all()
    create_all()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "create"
    {"create": create_all, "drop": drop_all, "reset": reset}.get(cmd, create_all)()
