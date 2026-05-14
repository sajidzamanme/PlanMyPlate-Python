from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import date

class UserBase(BaseModel):
    firstName: str = Field(alias="first_name")
    lastName: str = Field(alias="last_name")
    email: EmailStr
    phone: Optional[str] = None
    dateOfBirth: Optional[date] = Field(None, alias="date_of_birth")
    
    model_config = {"populate_by_name": True}

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        return v

class UserUpdate(BaseModel):
    firstName: Optional[str] = Field(None, alias="first_name")
    lastName: Optional[str] = Field(None, alias="last_name")
    phone: Optional[str] = None
    dateOfBirth: Optional[date] = Field(None, alias="date_of_birth")
    age: Optional[int] = None
    weight: Optional[Decimal] = None
    budget: Optional[Decimal] = None
    
    model_config = {"populate_by_name": True}

class UserDto(UserBase):
    userId: int = Field(alias="user_id")
    
    model_config = {"from_attributes": True, "populate_by_name": True}

class UserPreferencesDto(BaseModel):
    prefId: Optional[int] = Field(None, alias="pref_id")
    userId: int = Field(alias="user_id")
    diet: Optional[str] = None
    allergies: List[str] = []
    dislikes: List[str] = []
    budget: Optional[Decimal] = None
    height: Optional[Decimal] = None       # in cm
    weight: Optional[Decimal] = None       # in kg
    gender: Optional[str] = None           # male, female, other
    bmi: Optional[float] = None            # computed: weight(kg) / height(m)^2

    model_config = {"from_attributes": True, "populate_by_name": True}
