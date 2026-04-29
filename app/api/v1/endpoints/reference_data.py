from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from pydantic import BaseModel, Field

router = APIRouter()

class DietDto(BaseModel):
    dietId: int = Field(alias="diet_id")
    dietName: str = Field(alias="diet_name")

    model_config = {"from_attributes": True, "populate_by_name": True}

class AllergyDto(BaseModel):
    allergyId: int = Field(alias="allergy_id")
    allergyName: str = Field(alias="allergy_name")

    model_config = {"from_attributes": True, "populate_by_name": True}

class IngredientDto(BaseModel):
    ingId: int = Field(alias="ing_id")
    name: str

    model_config = {"from_attributes": True, "populate_by_name": True}

@router.get("/diets", response_model=List[DietDto])
def read_diets(
    db: Session = Depends(deps.get_db)
) -> Any:
    return crud.diet.get_multi(db)

@router.get("/allergies", response_model=List[AllergyDto])
def read_allergies(
    db: Session = Depends(deps.get_db)
) -> Any:
    return crud.allergy.get_multi(db)

@router.get("/dislikes", response_model=List[IngredientDto])
def read_dislikes(
    db: Session = Depends(deps.get_db)
) -> Any:
    return crud.ingredient.get_multi(db)
