from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from .ingredient import Ingredient

class InvItemCreateRequest(BaseModel):
    ingId: int = Field(alias="ing_id")
    quantity: float
    unit: str = "unit"
    expiryDate: Optional[date] = Field(None, alias="expiry_date")
    
    model_config = {"populate_by_name": True}

class InvItemResponse(BaseModel):
    itemId: int                     = Field(alias="item_id")
    ingredient: Ingredient
    quantity: Optional[float]         = None
    unit: Optional[str]             = None
    dateAdded: Optional[date]       = Field(None, alias="date_added")
    expiryDate: Optional[date]      = Field(None, alias="expiry_date")
    
    model_config = {"from_attributes": True, "populate_by_name": True}

class InventoryResponse(BaseModel):
    invId: int                  = Field(alias="inv_id")
    userId: int                 = Field(alias="user_id")
    lastUpdate: Optional[date]  = Field(None, alias="last_update")
    items: List[InvItemResponse] = []
    
    model_config = {"from_attributes": True, "populate_by_name": True}
