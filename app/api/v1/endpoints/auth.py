from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import secrets

from app import crud
from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.auth import (
    SignUpRequest, SignInRequest, AuthResponse, 
    ForgotPasswordRequest, ResetPasswordRequest, MessageResponse
)
from app.schemas.user import UserCreate

router = APIRouter()

@router.post("/signup", response_model=AuthResponse)
def sign_up(
    *,
    db: Session = Depends(deps.get_db),
    request: SignUpRequest
) -> Any:
    user = crud.user.get_by_email(db, email=request.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    user_in = UserCreate(
        email=request.email,
        password=request.password,
        name=request.name
    )
    user = crud.user.create(db, obj_in=user_in)
    
    access_token = security.create_access_token(user.email)
    
    return AuthResponse(
        token=access_token,
        email=user.email,
        name=user.name,
        userId=user.user_id
    )

@router.post("/signin", response_model=AuthResponse)
def sign_in(
    *,
    db: Session = Depends(deps.get_db),
    request: SignInRequest
) -> Any:
    user = crud.user.authenticate(
        db, email=request.email, password=request.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = security.create_access_token(user.email)
    
    return AuthResponse(
        token=access_token,
        access_token=access_token,
        token_type="bearer",
        email=user.email,
        name=user.name,
        userId=user.user_id
    )

@router.post("/token", response_model=AuthResponse)
def login_for_access_token(
    *,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = security.create_access_token(user.email)
    
    return AuthResponse(
        token=access_token,
        access_token=access_token,
        token_type="bearer",
        email=user.email,
        name=user.name,
        userId=user.user_id
    )

@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(
    *,
    db: Session = Depends(deps.get_db),
    request: ForgotPasswordRequest
) -> Any:
    user = crud.user.get_by_email(db, email=request.email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User with this email does not exist"
        )
    
    # Generate reset token
    reset_token = str(secrets.randbelow(9000) + 1000) # 4-digit numeric token
    user.reset_token = reset_token
    user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    db.add(user)
    db.commit()
    
    return MessageResponse(message=f"Password reset token sent to email. Token: {reset_token}")

@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    *,
    db: Session = Depends(deps.get_db),
    request: ResetPasswordRequest
) -> Any:
    user = db.query(crud.user.model).filter(crud.user.model.reset_token == request.resetToken).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    
    if not user.reset_token_expiry or datetime.now(timezone.utc) > user.reset_token_expiry:
        raise HTTPException(status_code=400, detail="Reset token expired")
    
    user.password = security.get_password_hash(request.newPassword)
    user.reset_token = None
    user.reset_token_expiry = None
    db.add(user)
    db.commit()
    
    return MessageResponse(message="Password reset successfully")
