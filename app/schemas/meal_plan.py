from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from .recipe import RecipeResponse

class MealPlanRequestDto(BaseModel):
    recipeIds: List[int] = Field(..., alias="recipe_ids")
    duration: int = 7
    startDate: Optional[date] = Field(None, alias="start_date")
    
    model_config = {"populate_by_name": True}

class MealSlotResponse(BaseModel):
    id: int
    slotIndex: int          = Field(alias="slot_index")
    mealType: str           = Field(alias="meal_type")
    dayNumber: int          = Field(alias="day_number")
    recipe: RecipeResponse
    
    model_config = {"from_attributes": True, "populate_by_name": True}

class MealPlanResponse(BaseModel):
    mpId: int                   = Field(alias="mp_id")
    userId: int                 = Field(alias="user_id")
    startDate: Optional[date]   = Field(None, alias="start_date")
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
