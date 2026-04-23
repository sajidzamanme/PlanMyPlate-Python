from pydantic import BaseModel, Field
from typing import List, Optional

class AiRecipeRequestDto(BaseModel):
    availableIngredients: List[str] = []
    maxCalories: Optional[int] = Field(None, ge=50, le=5000)
    cuisineType: Optional[str] = None
    allergies: List[str] = []
    dietaryPreference: Optional[str] = None
    mood: Optional[str] = None
    servings: int = Field(4, ge=1, le=20)
    maxCookingTime: Optional[int] = Field(None, ge=5, le=300)
