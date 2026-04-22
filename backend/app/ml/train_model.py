"""
train_model.py – Standalone script to train and save the project-type classifier.
Run from the backend/ directory:

    python -m app.ml.train_model

The saved model file (app/ml/project_type_model.pkl) is then loaded at runtime
by MLService without re-training.
"""

import sys
from pathlib import Path

# Ensure project root is on the path when run directly
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.services.ml_service import ml_service, MODEL_PATH


def main():
    print("=" * 55)
    print("  ProjectPilot – ML Model Trainer")
    print("=" * 55)

    if MODEL_PATH.exists():
        choice = input(f"\nModel already exists at {MODEL_PATH}.\nRetrain? [y/N]: ").strip().lower()
        if choice != "y":
            print("Skipping. Existing model retained.")
            return

    print("\n⏳ Training project-type classifier...")
    ml_service._train()  # Force re-train

    print(f"\n✅ Model saved to: {MODEL_PATH}")
    print(f"   Classes: {ml_service._classes}")

    # Quick smoke test
    test_ideas = [
        "An ecommerce store with cart and payment",
        "A real-time chat app for teams",
        "A machine learning model for image classification",
        "A content management system for blogs",
    ]
    print("\n🔍 Smoke tests:")
    print("-" * 55)
    for idea in test_ideas:
        result = ml_service.predict(idea)
        print(
            f"  Idea : {idea[:45]:<45}"
            f"  →  {result['project_type']:<14} "
            f"(conf: {result['confidence']:.2f})"
        )
    print("-" * 55)
    print("\n✅ Training complete. You can now start the backend server.\n")


if __name__ == "__main__":
    main()
