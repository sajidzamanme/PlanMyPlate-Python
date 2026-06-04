from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .recipe import RecipeResponse


class AddFavoriteRequest(BaseModel):
    recipeId: int


class UserFavoriteResponse(BaseModel):
    id: int
    userId: int = Field(validation_alias="user_id")
    recipeId: int = Field(validation_alias="recipe_id")
    recipe: Optional[RecipeResponse] = None
    createdAt: Optional[datetime] = Field(None, validation_alias="created_at")

    model_config = {"from_attributes": True, "populate_by_name": True}


class FavoriteStatusResponse(BaseModel):
    isFavorite: bool
