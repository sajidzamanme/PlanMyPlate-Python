from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from decimal import Decimal

class UserBase(BaseModel):
    name: str
    userName: Optional[str] = Field(None, alias="user_name")
    email: EmailStr
    
    model_config = {"populate_by_name": True}

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    userName: Optional[str] = Field(None, alias="user_name")
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
