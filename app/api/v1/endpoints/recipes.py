from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.schemas.recipe import RecipeResponse, RecipeCreateDto
from app.models.user import User

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

@router.post("/{id}/cook")
def cook_recipe(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    servings: float = 1.0,
    force: bool = False,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    recipe = crud.recipe.get(db, id=id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
        
    if not force:
        missing = crud.inventory.check_recipe_ingredients(db, user_id=current_user.user_id, recipe_id=id, servings=servings)
        if missing:
            return JSONResponse(
                status_code=409,
                content={
                    "status": "insufficient_ingredients",
                    "title": "Missing Pantry Items",
                    "message": "missing inventory item",
                    "missing": missing
                }
            )
            
    success = crud.inventory.deduct_recipe_ingredients(db, user_id=current_user.user_id, recipe_id=id, servings=servings)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to cook recipe")
    return {"message": "Recipe cooked and ingredients deducted from inventory"}

