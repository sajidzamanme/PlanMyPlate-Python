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
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    prepTime: Optional[int] = Field(None, ge=0, le=1440)
    cookTime: Optional[int] = Field(None, ge=0, le=1440)
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
    recipeId: int       = Field(validation_alias="recipe_id")
    name: str
    description: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    prepTime: Optional[int]  = Field(None, validation_alias="prep_time")
    cookTime: Optional[int]  = Field(None, validation_alias="cook_time")
    instructions: Optional[str] = None
    imageUrl: Optional[str]  = Field(None, validation_alias="image_url")
    recipeIngredients: List[RecipeIngredientResponse] = Field([], validation_alias="recipe_ingredients")
    isDeleted: bool = Field(False, validation_alias="is_deleted")
    
    model_config = {"from_attributes": True, "populate_by_name": True}
