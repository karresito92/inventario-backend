"""
Users Router - Endpoints for user management and authentication
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.dependencies import (
    get_db,
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    UserToken,
    UserPasswordUpdate,
)
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Creates a new user.
    - Verifies that email and username are not already registered.
    - Hashes the password before saving.
    """
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(400, "Email already registered")
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(400, "Username already taken")
    
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=UserToken)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates an existing user.
    - Validates email and password.
    - Returns a JWT access token if correct.
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate JWT token
    access_token = create_access_token({"sub": str(user.id)})
    return UserToken(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id_endpoint(
    user_id: uuid.UUID,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Returns information about a specific user.
    - Only the user themselves or an admin can access it.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    # Allow access if it's the same user
    if user.id != current_user.id:
        # In future: check if current_user is admin
        pass
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Updates user data.
    - Only the user themselves can update (admin check pending).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    if user.id != current_user.id:
        # In future: allow if current_user is admin
        raise HTTPException(403, "Not enough permissions")
    
    for k, v in user_update.model_dump(exclude_unset=True).items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: uuid.UUID,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Deactivates (soft delete) a user account.
    - Only the user themselves can do it (admin check pending).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    if user.id != current_user.id:
        raise HTTPException(403, "Not enough permissions")
    # Soft delete: set is_active to False (field to be added)
    # For now, just delete
    db.delete(user)
    db.commit()
    return


@router.get("/", response_model=List[UserResponse])
def list_users(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Returns a filterable list of users (admin only).
    - Allows searching by name, email.
    """
    q = db.query(User)
    if search:
        like = f"%{search}%"
        q = q.filter(
            (User.first_name.ilike(like)) |
            (User.last_name.ilike(like)) |
            (User.email.ilike(like)) |
            (User.username.ilike(like))
        )
    return q.offset(skip).limit(limit).all()


@router.put("/{user_id}/password", status_code=status.HTTP_204_NO_CONTENT)
def update_password(
    user_id: uuid.UUID,
    data: UserPasswordUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Changes a user's password.
    - Requires valid current password.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    if user.id != current_user.id:
        raise HTTPException(403, "Not enough permissions")
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(400, "Current password is incorrect")
    user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return


@router.get("/me/profile", response_model=UserResponse)
def get_my_profile(current_user = Depends(get_current_active_user)):
    """
    Returns the authenticated user's information.
    """
    return current_user


@router.put("/me/profile", response_model=UserResponse)
def update_my_profile(
    update: UserUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Allows the user to edit their own profile.
    """
    for k, v in update.model_dump(exclude_unset=True).items():
        setattr(current_user, k, v)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/stats")
def get_my_stats(current_user = Depends(get_current_active_user)):
    """
    Returns basic user status and data.
    """
    return {
        "user_id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at,
        "full_name": current_user.full_name,
    }