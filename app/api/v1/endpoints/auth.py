from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
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
    # Check for duplicate email
    user = crud.user.get_by_email(db, email=request.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    # Check for duplicate phone
    existing_phone = crud.user.get_by_phone(db, phone=request.phone)
    if existing_phone:
        raise HTTPException(
            status_code=400,
            detail="User with this phone number already exists"
        )
    
    user_in = UserCreate(
        email=request.email,
        password=request.password,
        firstName=request.firstName,
        lastName=request.lastName,
        phone=request.phone,
        dateOfBirth=request.dateOfBirth
    )
    user = crud.user.create(db, obj_in=user_in)
    
    access_token = security.create_access_token(user.email)
    
    return AuthResponse(
        access_token=access_token,
        email=user.email,
        firstName=user.first_name,
        lastName=user.last_name,
        userId=user.user_id,
        phone=user.phone,
        dateOfBirth=user.date_of_birth
    )

@router.post("/signin", response_model=AuthResponse)
def sign_in(
    *,
    db: Session = Depends(deps.get_db),
    request: SignInRequest
) -> Any:
    user = crud.user.authenticate(
        db, identifier=request.email, password=request.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email/phone or password")
    
    access_token = security.create_access_token(user.email)
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        email=user.email,
        firstName=user.first_name,
        lastName=user.last_name,
        userId=user.user_id,
        phone=user.phone,
        dateOfBirth=user.date_of_birth
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
    
    # Clear "0000" reset token for any other user to prevent lookup conflicts
    db.query(crud.user.model).filter(crud.user.model.reset_token == "0000").update(
        {"reset_token": None, "reset_token_expiry": None},
        synchronize_session=False
    )
    
    # Generate reset token (always "0000" as requested)
    reset_token = "0000"
    user.reset_token = reset_token
    user.reset_token_expiry = datetime.now() + timedelta(hours=1)
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
    
    # Compare local naive datetimes to avoid timezone-aware vs naive mismatch
    current_time = datetime.now()
    if not user.reset_token_expiry or current_time > user.reset_token_expiry:
        raise HTTPException(status_code=400, detail="Reset token expired")
    
    user.password = security.get_password_hash(request.newPassword)
    user.reset_token = None
    user.reset_token_expiry = None
    db.add(user)
    db.commit()
    
    return MessageResponse(message="Password reset successfully")
