from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import date
import re

class SignUpRequest(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    phone: str
    dateOfBirth: date = Field(..., validation_alias="dateOfBirth")

    model_config = {"populate_by_name": True}

    @field_validator("firstName")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("First name cannot be empty")
        return v.strip()

    @field_validator("lastName")
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Last name cannot be empty")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Strip common formatting, then validate
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(r"^\+?\d{7,15}$", cleaned):
            raise ValueError("Phone number must be 7-15 digits, optionally starting with +")
        return cleaned

    @field_validator("dateOfBirth")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError("Date of birth must be in the past")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        return v

class SignInRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    firstName: str
    lastName: str
    userId: int
    phone: Optional[str] = None
    dateOfBirth: Optional[date] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    resetToken: str
    newPassword: str

    @field_validator("newPassword")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        return v

class MessageResponse(BaseModel):
    message: str
