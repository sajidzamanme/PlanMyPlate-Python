from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any
from datetime import date
from .ingredient import Ingredient

class GroceryListCreate(BaseModel):
    status: str = "active"

class GroceryListItemResponse(BaseModel):
    id: int
    ingredient: Ingredient
    quantity: Optional[float] = None
    unit: Optional[str] = None
    
    model_config = {"from_attributes": True}

class GroceryListResponse(BaseModel):
    listId: int                     = Field(validation_alias="list_id")
    userId: int                     = Field(validation_alias="user_id")
    dateCreated: Optional[date]     = Field(None, validation_alias="date_created")
    status: Optional[str]           = None
    items: List[GroceryListItemResponse] = []
    
    model_config = {"from_attributes": True, "populate_by_name": True}

    @field_validator("items", mode="before")
    @classmethod
    def sort_items(cls, v: Any) -> Any:
        if isinstance(v, list):
            def get_name(item):
                if hasattr(item, "ingredient") and item.ingredient:
                    return getattr(item.ingredient, "name", "") or ""
                elif isinstance(item, dict):
                    ing = item.get("ingredient", {})
                    if isinstance(ing, dict):
                        return ing.get("name", "") or ""
                    elif hasattr(ing, "name"):
                        return getattr(ing, "name", "") or ""
                return ""
            return sorted(v, key=lambda x: get_name(x).lower())
        return v

class PurchaseItemInfo(BaseModel):
    itemId: int
    quantity: float

class PurchaseRequestDto(BaseModel):
    items: List[PurchaseItemInfo]

class UpdateItemRequestDto(BaseModel):
    quantity: Optional[float] = None
    unit: Optional[str] = None
    expiryDate: Optional[date] = None
