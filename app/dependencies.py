"""
Dependencies - Shared dependencies for routers (Auth, DB session, etc.)
"""

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# CONFIGURACIÓN
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://postgres:password123@db:5432/becarios_db"
)
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-demo-key")
JWT_ALG = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

# Database engine
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


# DEPENDENCY: Database session
def get_db() -> Session:
    """Provides a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# PASSWORD UTILITIES
def get_password_hash(password: str) -> str:
    """Returns a secure hash of the password"""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verifies if a password matches its hash"""
    return pwd_context.verify(plain, hashed)


# JWT UTILITIES
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a JWT access token with expiration"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)


# USER UTILITIES (These will need to import User model after we create it)
def get_user_by_id(db: Session, user_id: uuid.UUID):
    """Gets a user by ID - TO BE IMPLEMENTED with actual User model"""
    from app.models.user import User
    return db.query(User).filter(User.id == user_id).first()
    pass


def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    """Gets the authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        sub: str = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = uuid.UUID(sub)
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise credentials_exception
    return user


def get_current_active_user(current_user = Depends(get_current_user)):
    """Verifies that the user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="User account is inactive")

    return current_user


def get_current_admin_user(current_user = Depends(get_current_active_user)):
    """Restricts access to administrators only"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return current_user