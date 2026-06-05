from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any
from datetime import date
from .ingredient import Ingredient

class InvItemCreateRequest(BaseModel):
    ingId: int = Field(validation_alias="ing_id")
    quantity: float
    unit: str = "unit"
    expiryDate: Optional[date] = Field(None, validation_alias="expiry_date")
    
    model_config = {"populate_by_name": True}

class InvItemResponse(BaseModel):
    itemId: int                     = Field(validation_alias="item_id")
    ingredient: Ingredient
    quantity: Optional[float]         = None
    unit: Optional[str]             = None
    dateAdded: Optional[date]       = Field(None, validation_alias="date_added")
    expiryDate: Optional[date]      = Field(None, validation_alias="expiry_date")
    
    model_config = {"from_attributes": True, "populate_by_name": True}

class InventoryResponse(BaseModel):
    invId: int                  = Field(validation_alias="inv_id")
    userId: int                 = Field(validation_alias="user_id")
    lastUpdate: Optional[date]  = Field(None, validation_alias="last_update")
    items: List[InvItemResponse] = []
    
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
