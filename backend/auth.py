# backend/auth.py
# Handles register, login, JWT

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import get_db
from models import User


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "fallback-secret"
)

ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256"
)

EXPIRE_MIN = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        60
    )
)


# ---------------------------------------------------------
# Password hashing
# ---------------------------------------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# Bcrypt has a maximum input size of 72 bytes.
BCRYPT_MAX_BYTES = 72


def password_is_valid_length(password: str) -> bool:
    """
    Check the UTF-8 byte length of the password.

    Bcrypt supports a maximum of 72 bytes.
    """

    return len(
        password.encode("utf-8")
    ) <= BCRYPT_MAX_BYTES


def hash_password(password: str) -> str:
    """
    Hash a password only if it fits bcrypt's
    maximum input size.
    """

    if not password_is_valid_length(password):
        raise ValueError(
            "Password must be 72 bytes or fewer."
        )

    return pwd_context.hash(password)


def verify_password(
    plain: str,
    hashed: str
) -> bool:
    """
    Safely verify a password.

    Overlong passwords are rejected before
    reaching bcrypt.
    """

    if not password_is_valid_length(plain):
        return False

    try:
        return pwd_context.verify(
            plain,
            hashed
        )

    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------

class UserCreate(BaseModel):

    full_name: str
    email: EmailStr
    password: str
    risk_profile: str = "moderate"


class Token(BaseModel):

    access_token: str
    token_type: str


# ---------------------------------------------------------
# Database helpers
# ---------------------------------------------------------

def get_user_by_email(
    db: Session,
    email: str
):
    return (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


# ---------------------------------------------------------
# JWT
# ---------------------------------------------------------

def create_access_token(
    data: dict
) -> str:

    payload = data.copy()

    payload["exp"] = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=EXPIRE_MIN
        )
    )

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ---------------------------------------------------------
# Register
# ---------------------------------------------------------

def register_user(
    data: UserCreate,
    db: Session
):

    if get_user_by_email(
        db,
        data.email
    ):

        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )


    if data.risk_profile not in (
        "conservative",
        "moderate",
        "aggressive"
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid risk profile."
        )


    # Check password BEFORE bcrypt
    if not password_is_valid_length(
        data.password
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Password must be 72 bytes or fewer."
            )
        )


    try:

        hashed_password = hash_password(
            data.password
        )

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail=(
                "Password must be 72 bytes or fewer."
            )
        )


    user = User(
        full_name=data.full_name,
        email=data.email.lower(),
        hashed_password=hashed_password,
        risk_profile=data.risk_profile,
    )


    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

def login_user(
    email: str,
    password: str,
    db: Session
):

    user = get_user_by_email(
        db,
        email.lower()
    )


    # This also safely handles passwords
    # longer than 72 bytes.
    if not user or not verify_password(
        password,
        user.hashed_password
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


    token = create_access_token(
        {
            "sub": user.email
        }
    )


    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ---------------------------------------------------------
# Current authenticated user
# ---------------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get(
            "sub"
        )

        if not email:

            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


    user = get_user_by_email(
        db,
        email
    )


    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )


    return user