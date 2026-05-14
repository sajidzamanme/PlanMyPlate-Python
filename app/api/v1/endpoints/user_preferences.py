from typing import Any, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.schemas.user import UserPreferencesDto
from app.models.user import User

router = APIRouter()


def _calculate_bmi(height: Optional[Decimal], weight: Optional[Decimal]) -> Optional[float]:
    """Calculate BMI from height (cm) and weight (kg)."""
    if height and weight and height > 0:
        height_m = float(height) / 100.0
        return round(float(weight) / (height_m ** 2), 1)
    return None


def _build_prefs_dto(prefs) -> UserPreferencesDto:
    """Build a UserPreferencesDto from a UserPreferences model instance."""
    bmi = _calculate_bmi(prefs.height, prefs.weight)
    return UserPreferencesDto(
        prefId=prefs.pref_id,
        userId=prefs.user_id,
        diet=prefs.diet.diet_name if prefs.diet else None,
        allergies=[a.name for a in prefs.allergies],
        dislikes=[d.name for d in prefs.dislikes],
        budget=prefs.budget,
        height=prefs.height,
        weight=prefs.weight,
        gender=prefs.gender,
        bmi=bmi
    )


@router.get("/{user_id}", response_model=UserPreferencesDto)
def get_preferences(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Allow users to view their own preferences
    if user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    prefs = crud.user_preferences.get_by_user_id(db, user_id=user_id)
    if not prefs:
        # Return default if not found
        return UserPreferencesDto(userId=user_id, allergies=[], dislikes=[])
    
    return _build_prefs_dto(prefs)

@router.post("/{user_id}", response_model=UserPreferencesDto)
def set_preferences(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    prefs_in: UserPreferencesDto,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    prefs = crud.user_preferences.create_or_update(db, user_id=user_id, obj_in=prefs_in)
    
    return _build_prefs_dto(prefs)

