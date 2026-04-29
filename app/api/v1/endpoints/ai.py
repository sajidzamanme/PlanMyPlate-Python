from typing import Any, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.ai import AiRecipeRequestDto
from app.schemas.recipe import RecipeResponse
from app.schemas.meal_plan import MealPlanResponse
from app.services.gemini_service import gemini_service
from app.models.user import User

router = APIRouter()

@router.post("/generate-recipe", response_model=RecipeResponse, status_code=201)
def generate_recipe(
    *,
    db: Session = Depends(deps.get_db),
    request: AiRecipeRequestDto,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    return gemini_service.generate_recipe(db, request=request)

@router.post("/generate-meal-plan", response_model=MealPlanResponse, status_code=201)
def generate_meal_plan(
    *,
    db: Session = Depends(deps.get_db),
    userId: int,
    startDate: Optional[date] = Query(None, description="Start date in YYYY-MM-DD format (defaults to today)"),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if userId != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return gemini_service.generate_weekly_meal_plan(db, user_id=userId, start_date=startDate)
