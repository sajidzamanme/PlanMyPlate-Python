from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas.user import UserDto
from app.schemas.ingredient import Ingredient, IngredientCreate, IngredientUpdate
from app.schemas.recipe import RecipeResponse, RecipeCreateDto
from app.models.user import User

router = APIRouter(tags=["admin"])


# ── Users ──────────────────────────────────────────────────────────────────────

@router.get("/users/{user_id}", response_model=UserDto)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserDto(
        userId=user.user_id,
        email=user.email,
        firstName=user.first_name,
        lastName=user.last_name,
        phone=user.phone,
        dateOfBirth=user.date_of_birth,
    )


# ── Ingredients ────────────────────────────────────────────────────────────────

@router.post("/ingredients", response_model=Ingredient, status_code=201)
def create_ingredient(
    *,
    db: Session = Depends(deps.get_db),
    ingredient_in: IngredientCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    return crud.ingredient.create(db, obj_in=ingredient_in)


@router.put("/ingredients/{id}", response_model=Ingredient)
def update_ingredient(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    ingredient_in: IngredientUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    ingredient = crud.ingredient.get(db, id=id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return crud.ingredient.update(db, db_obj=ingredient, obj_in=ingredient_in)


@router.delete("/ingredients/{id}")
def delete_ingredient(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    ingredient = crud.ingredient.get(db, id=id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    crud.ingredient.remove(db, id=id)
    return {"message": "Ingredient deleted successfully"}


# ── Recipes ────────────────────────────────────────────────────────────────────

@router.put("/recipes/{id}", response_model=RecipeResponse)
def update_recipe(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    recipe_in: RecipeCreateDto,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    recipe = crud.recipe.get(db, id=id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return crud.recipe.update_recipe(db, db_obj=recipe, obj_in=recipe_in)


@router.delete("/recipes/{id}")
def delete_recipe(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    recipe = crud.recipe.get(db, id=id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    crud.recipe.remove(db, id=id)
    return {"message": "Recipe deleted successfully"}
