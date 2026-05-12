from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.models.user import User
from app.schemas.favorite import (
    UserFavoriteResponse,
    FavoriteStatusResponse,
)

router = APIRouter()


@router.post("/{recipe_id}", response_model=UserFavoriteResponse, status_code=201)
def add_favorite(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    recipe_id: int,
) -> Any:
    """Add a recipe to the current user's favorites."""
    recipe = crud.recipe.get(db, id=recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return crud.favorite.add_favorite(
        db, user_id=current_user.user_id, recipe_id=recipe_id
    )


@router.delete("/{recipe_id}")
def remove_favorite(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    recipe_id: int,
) -> Any:
    """Remove a recipe from the current user's favorites."""
    removed = crud.favorite.remove_favorite(
        db, user_id=current_user.user_id, recipe_id=recipe_id
    )
    if not removed:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"message": "Favorite removed successfully"}


@router.get("/", response_model=List[UserFavoriteResponse])
def get_my_favorites(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """List the current user's favorite recipes."""
    return crud.favorite.get_user_favorites(
        db, user_id=current_user.user_id, skip=skip, limit=limit
    )


@router.get("/{recipe_id}/status", response_model=FavoriteStatusResponse)
def check_favorite_status(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    recipe_id: int,
) -> Any:
    """Check whether a recipe is in the current user's favorites."""
    is_fav = crud.favorite.is_favorite(
        db, user_id=current_user.user_id, recipe_id=recipe_id
    )
    return {"isFavorite": is_fav}
