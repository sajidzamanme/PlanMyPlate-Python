from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from .ingredient import Ingredient

class GroceryListCreate(BaseModel):
    status: str = "active"

class GroceryListItemResponse(BaseModel):
    id: int
    ingredient: Ingredient
    quantity: Optional[int] = None
    unit: Optional[str] = None
    
    model_config = {"from_attributes": True}

class GroceryListResponse(BaseModel):
    listId: int                     = Field(alias="list_id")
    userId: int                     = Field(alias="user_id")
    dateCreated: Optional[date]     = Field(None, alias="date_created")
    status: Optional[str]           = None
    items: List[GroceryListItemResponse] = []
    
    model_config = {"from_attributes": True, "populate_by_name": True}

class PurchaseItemInfo(BaseModel):
    itemId: int
    quantity: int

class PurchaseRequestDto(BaseModel):
    items: List[PurchaseItemInfo]

class UpdateItemRequestDto(BaseModel):
    quantity: Optional[int] = None
    unit: Optional[str] = None
    expiryDate: Optional[date] = None
