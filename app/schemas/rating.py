from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RateRecipeRequest(BaseModel):
    recipeId: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    review: Optional[str] = None


class RecipeRatingResponse(BaseModel):
    ratingId: int = Field(alias="rating_id")
    userId: int = Field(alias="user_id")
    recipeId: int = Field(alias="recipe_id")
    rating: int
    review: Optional[str] = None
    createdAt: Optional[datetime] = Field(None, alias="created_at")
    updatedAt: Optional[datetime] = Field(None, alias="updated_at")

    model_config = {"from_attributes": True, "populate_by_name": True}


class RecipeRatingSummary(BaseModel):
    recipeId: int
    averageRating: float
    totalRatings: int
