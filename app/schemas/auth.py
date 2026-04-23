from pydantic import BaseModel, EmailStr
from typing import Optional

class SignUpRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    token: str
    access_token: Optional[str] = None # Added for Swagger compatibility
    token_type: str = "bearer"         # Added for Swagger compatibility
    email: str
    name: str
    userId: int

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    resetToken: str
    newPassword: str

class MessageResponse(BaseModel):
    message: str
