from pydantic import BaseModel, Field
from typing import List, Optional
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
