from pydantic import BaseModel, Field
from typing import List, Optional
from .ingredient import Ingredient

class RecipeIngredientDto(BaseModel):
    ingId: int
    quantity: Optional[float] = 1.0
    unit: Optional[str] = "unit"

class RecipeCreateDto(BaseModel):
    name: str
    description: Optional[str] = None
    calories: Optional[int] = Field(None, ge=50, le=5000)
    prepTime: Optional[int] = Field(None, ge=0, le=1440)
    cookTime: Optional[int] = Field(None, ge=0, le=1440)
    servings: Optional[int] = Field(1, ge=1, le=50)
    instructions: Optional[str] = None
    imageUrl: Optional[str] = None
    ingredients: List[RecipeIngredientDto] = []

class RecipeIngredientResponse(BaseModel):
    id: int
    ingredient: Ingredient
    quantity: Optional[float] = None
    unit: Optional[str] = None
    
    model_config = {"from_attributes": True}

class RecipeResponse(BaseModel):
    recipeId: int       = Field(alias="recipe_id")
    name: str
    description: Optional[str] = None
    calories: Optional[int] = None
    prepTime: Optional[int]  = Field(None, alias="prep_time")
    cookTime: Optional[int]  = Field(None, alias="cook_time")
    servings: Optional[int] = None
    instructions: Optional[str] = None
    imageUrl: Optional[str]  = Field(None, alias="image_url")
    recipeIngredients: List[RecipeIngredientResponse] = Field([], alias="recipe_ingredients")
    
    model_config = {"from_attributes": True, "populate_by_name": True}

