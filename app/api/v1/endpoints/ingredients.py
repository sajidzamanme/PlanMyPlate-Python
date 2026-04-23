from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.schemas.ingredient import Ingredient, IngredientCreate, IngredientUpdate

router = APIRouter()

@router.get("/", response_model=List[Ingredient])
def read_ingredients(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    return crud.ingredient.get_multi(db, skip=skip, limit=limit)

@router.get("/search", response_model=List[Ingredient])
def search_ingredients(
    *,
    db: Session = Depends(deps.get_db),
    name: str
) -> Any:
    return crud.ingredient.search_by_name(db, name=name)

@router.get("/filter/price", response_model=List[Ingredient])
def filter_ingredients_by_price(
    *,
    db: Session = Depends(deps.get_db),
    minPrice: float = Query(..., alias="minPrice"),
    maxPrice: float = Query(..., alias="maxPrice")
) -> Any:
    return crud.ingredient.filter_by_price(db, min_price=minPrice, max_price=maxPrice)

@router.post("/", response_model=Ingredient, status_code=201)
def create_ingredient(
    *,
    db: Session = Depends(deps.get_db),
    ingredient_in: IngredientCreate
) -> Any:
    return crud.ingredient.create(db, obj_in=ingredient_in)

@router.get("/{id}", response_model=Ingredient)
def read_ingredient(
    *,
    db: Session = Depends(deps.get_db),
    id: int
) -> Any:
    ingredient = crud.ingredient.get(db, id=id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient

@router.put("/{id}", response_model=Ingredient)
def update_ingredient(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    ingredient_in: IngredientUpdate
) -> Any:
    ingredient = crud.ingredient.get(db, id=id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return crud.ingredient.update(db, db_obj=ingredient, obj_in=ingredient_in)

@router.delete("/{id}")
def delete_ingredient(
    *,
    db: Session = Depends(deps.get_db),
    id: int
) -> Any:
    ingredient = crud.ingredient.get(db, id=id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    crud.ingredient.remove(db, id=id)
    return {"message": "Ingredient deleted successfully"}
