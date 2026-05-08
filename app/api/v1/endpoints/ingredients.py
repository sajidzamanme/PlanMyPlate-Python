from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.schemas.ingredient import Ingredient

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


