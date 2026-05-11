from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from loguru import logger

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, Token
from app.core.security import hash_password, verify_password, create_access_token
from app.services.activity_service import activity_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, request: Request, db: Session = Depends(get_db)):
    """Register a new user and return an access token."""
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken.")

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"New user registered: {user.email}")

    # Log user signup activity
    try:
        activity_service.log_activity(
            db=db,
            action="user_signup",
            user_id=user.id,
            description=f"New user registered: {user.username}",
            metadata={"email": user.email, "username": user.username},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
    except Exception as e:
        logger.warning(f"Failed to log signup activity: {e}")

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(payload: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Authenticate and return an access token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated.")

    # Log user login activity
    try:
        activity_service.log_activity(
            db=db,
            action="user_login",
            user_id=user.id,
            description=f"User logged in: {user.username}",
            metadata={"email": user.email, "username": user.username},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
    except Exception as e:
        logger.warning(f"Failed to log login activity: {e}")

    token = create_access_token({"sub": str(user.id)})
    logger.info(f"User logged in: {user.email}")
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return current_user
