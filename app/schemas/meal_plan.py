from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from .recipe import RecipeResponse

class MealPlanRequestDto(BaseModel):
    recipeIds: List[int] = Field(..., validation_alias="recipe_ids")
    servingsMultipliers: Optional[List[int]] = Field(None, validation_alias="servings_multipliers")
    duration: int = 7
    startDate: Optional[date] = Field(None, validation_alias="start_date")
    
    model_config = {"populate_by_name": True}

class MealSlotResponse(BaseModel):
    id: int
    slotIndex: int          = Field(validation_alias="slot_index")
    mealType: str           = Field(validation_alias="meal_type")
    dayNumber: int          = Field(validation_alias="day_number")
    servingsMultiplier: int = Field(validation_alias="servings_multiplier", default=1)
    recipe: RecipeResponse
    
    model_config = {"from_attributes": True, "populate_by_name": True}

class MealPlanResponse(BaseModel):
    mpId: int                   = Field(validation_alias="mp_id")
    userId: int                 = Field(validation_alias="user_id")
    startDate: Optional[date]   = Field(None, validation_alias="start_date")
    duration: Optional[int]     = None
    status: Optional[str]       = None
    slots: List[MealSlotResponse] = []
    
    model_config = {"from_attributes": True, "populate_by_name": True}

class MealPlanCreate(BaseModel):
    startDate: Optional[date] = None
    duration: int = 7
    status: str = "active"

class MealPlanUpdate(BaseModel):
    status: Optional[str] = None
    duration: Optional[int] = None
