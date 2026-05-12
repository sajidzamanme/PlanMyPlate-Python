from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.models.user import User
from app.schemas.rating import (
    RateRecipeRequest,
    RecipeRatingResponse,
    RecipeRatingSummary,
)

router = APIRouter()


@router.post("/", response_model=RecipeRatingResponse, status_code=201)
def rate_recipe(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    body: RateRecipeRequest,
) -> Any:
    """Rate a recipe (creates or updates the rating)."""
    # Verify recipe exists
    recipe = crud.recipe.get(db, id=body.recipeId)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return crud.rating.upsert_rating(
        db,
        user_id=current_user.user_id,
        recipe_id=body.recipeId,
        rating=body.rating,
        review=body.review,
    )


@router.get("/my/{recipe_id}", response_model=RecipeRatingResponse)
def get_my_rating(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    recipe_id: int,
) -> Any:
    """Get the current user's rating for a specific recipe."""
    rating = crud.rating.get_user_rating(
        db, user_id=current_user.user_id, recipe_id=recipe_id
    )
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating


@router.get("/recipe/{recipe_id}", response_model=RecipeRatingSummary)
def get_recipe_rating_summary(
    *,
    db: Session = Depends(deps.get_db),
    recipe_id: int,
) -> Any:
    """Get the average rating and total number of ratings for a recipe."""
    recipe = crud.recipe.get(db, id=recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return crud.rating.get_rating_summary(db, recipe_id=recipe_id)


@router.delete("/{recipe_id}")
def delete_my_rating(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    recipe_id: int,
) -> Any:
    """Delete the current user's rating for a recipe."""
    deleted = crud.rating.delete_rating(
        db, user_id=current_user.user_id, recipe_id=recipe_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Rating not found")
    return {"message": "Rating deleted successfully"}
