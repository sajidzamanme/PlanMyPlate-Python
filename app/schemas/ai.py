from pydantic import BaseModel, Field
from typing import List, Optional

class AiRecipeRequestDto(BaseModel):
    availableIngredients: List[str] = []
    tags: List[str] = []
    useInventory: bool = Field(False, validation_alias="useInventory")
    maxCalories: Optional[int] = Field(None, ge=50, le=5000)
    cuisineType: Optional[str] = None
    allergies: List[str] = []
    dietaryPreference: Optional[str] = None
    mood: Optional[str] = None
    maxCookingTime: Optional[int] = Field(None, ge=5, le=300)

    model_config = {"populate_by_name": True}
