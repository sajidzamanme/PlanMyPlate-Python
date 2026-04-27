from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.schemas.recipe import RecipeResponse, RecipeCreateDto

router = APIRouter()

@router.get("/", response_model=List[RecipeResponse])
def read_recipes(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    return crud.recipe.get_multi(db, skip=skip, limit=limit)

@router.get("/search", response_model=List[RecipeResponse])
def search_recipes(
    *,
    db: Session = Depends(deps.get_db),
    name: str
) -> Any:
    return crud.recipe.search_by_name(db, name=name)

@router.get("/filter/calories", response_model=List[RecipeResponse])
def filter_recipes_by_calories(
    *,
    db: Session = Depends(deps.get_db),
    minCalories: int = Query(..., alias="minCalories"),
    maxCalories: int = Query(..., alias="maxCalories")
) -> Any:
    return crud.recipe.filter_by_calories(db, min_cals=minCalories, max_cals=maxCalories)

@router.post("/", response_model=RecipeResponse, status_code=201)
def create_recipe(
    *,
    db: Session = Depends(deps.get_db),
    recipe_in: RecipeCreateDto
) -> Any:
    return crud.recipe.create_recipe(db, obj_in=recipe_in)

@router.get("/{id}", response_model=RecipeResponse)
def read_recipe(
    *,
    db: Session = Depends(deps.get_db),
    id: int
) -> Any:
    recipe = crud.recipe.get(db, id=id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.put("/{id}", response_model=RecipeResponse)
def update_recipe(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    recipe_in: RecipeCreateDto
) -> Any:
    recipe = crud.recipe.get(db, id=id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return crud.recipe.update_recipe(db, db_obj=recipe, obj_in=recipe_in)

@router.delete("/{id}")
def delete_recipe(
    *,
    db: Session = Depends(deps.get_db),
    id: int
) -> Any:
    recipe = crud.recipe.get(db, id=id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    crud.recipe.remove(db, id=id)
    return {"message": "Recipe deleted successfully"}
