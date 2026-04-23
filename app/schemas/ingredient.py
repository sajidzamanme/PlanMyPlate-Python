from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal

class IngredientTag(BaseModel):
    tagId: int = Field(alias="tag_id")
    tagName: str = Field(alias="tag_name")
    
    model_config = {"from_attributes": True, "populate_by_name": True}

class IngredientBase(BaseModel):
    name: str
    price: Optional[Decimal] = None

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None

class Ingredient(IngredientBase):
    ingId: int = Field(alias="ing_id")
    tags: List[IngredientTag] = []
    
    model_config = {"from_attributes": True, "populate_by_name": True}

class IngredientQuantityDto(BaseModel):
    ingredient: Ingredient
    quantity: int
    unit: str
    
    model_config = {"from_attributes": True, "populate_by_name": True}
