from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from decimal import Decimal
from datetime import date

class UserBase(BaseModel):
    firstName: str = Field(alias="first_name")
    lastName: str = Field(alias="last_name")
    userName: Optional[str] = Field(None, alias="user_name")
    email: EmailStr
    phone: Optional[str] = None
    dateOfBirth: Optional[date] = Field(None, alias="date_of_birth")
    
    model_config = {"populate_by_name": True}

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    firstName: Optional[str] = Field(None, alias="first_name")
    lastName: Optional[str] = Field(None, alias="last_name")
    userName: Optional[str] = Field(None, alias="user_name")
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
    servings: int
    budget: Optional[Decimal] = None

    model_config = {"from_attributes": True, "populate_by_name": True}
