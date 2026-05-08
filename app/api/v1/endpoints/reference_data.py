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

@router.get("/diets", response_model=List[DietDto])
def read_diets(
    db: Session = Depends(deps.get_db)
) -> Any:
    return crud.diet.get_multi(db)
