import re
import socket
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from app.security import verify_password, get_password_hash, create_access_token
from app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


def validate_real_email_domain(email: str) -> None:
    """
    Validate that an email address has a real, reachable domain and is not a common typo or fake domain.
    Raises HTTPException 400 with a user-friendly error message if invalid.
    """
    # 1. Basic format check
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a valid email address."
        )

    parts = email.split("@")
    if len(parts) != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a valid email address."
        )

    domain = parts[1].strip().lower()

    # 2. Common domain typos
    common_typos = {
        "gmaill.com": "gmail.com",
        "gamil.com": "gmail.com",
        "gmal.com": "gmail.com",
        "gmai.com": "gmail.com",
        "gmaildotcom": "gmail.com",
        "yaho.com": "yahoo.com",
        "yahooo.com": "yahoo.com",
        "hotmial.com": "hotmail.com",
        "hotmai.com": "hotmail.com",
        "outlok.com": "outlook.com",
        "outllok.com": "outlook.com",
    }
    if domain in common_typos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid email domain. Did you mean @{common_typos[domain]}?"
        )

    # 3. Block known fake/throwaway/test domains
    blocked_domains = {
        "fake.com", "test.com", "example.com", "sample.com", "invalid.com",
        "tempmail.com", "mailinator.com", "10minutemail.com", "guerrillamail.com",
        "throwawaymail.com", "trashmail.com", "yopmail.com", "dispostable.com"
    }
    if domain in blocked_domains:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Temporary or disposable email domains are not allowed. Please use a valid email."
        )

    # 4. Check domain DNS resolution to ensure it actually exists on the internet
    try:
        socket.getaddrinfo(domain, 80, proto=socket.IPPROTO_TCP)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The email domain '@{domain}' does not exist. Please enter a valid, active email address."
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account with validated email and minimum 8-character password."""
    # Validate email authenticity & domain existence
    validate_real_email_domain(user_in.email)

    # Check if user with normalized email already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    # Hash the password and save the new user
    hashed_password = get_password_hash(user_in.password)
    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user credentials and issue a signed JWT access token."""
    user = db.query(User).filter(User.email == user_in.email).first()

    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve profile details of the currently authenticated user."""
    return current_user
