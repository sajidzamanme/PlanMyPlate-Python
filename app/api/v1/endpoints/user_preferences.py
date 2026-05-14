from typing import Any, Optional
from decimal import Decimal
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.schemas.user import UserPreferencesDto
from app.models.user import User

router = APIRouter()


def _calculate_age(date_of_birth: Optional[date]) -> Optional[int]:
    """Calculate age in years from date of birth."""
    if not date_of_birth:
        return None
    today = date.today()
    age = today.year - date_of_birth.year
    # Adjust if birthday hasn't occurred yet this year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    return age


def _calculate_bmi(height: Optional[Decimal], weight: Optional[Decimal]) -> Optional[float]:
    """Calculate BMI from height (cm) and weight (kg)."""
    if height and weight and height > 0:
        height_m = float(height) / 100.0
        return round(float(weight) / (height_m ** 2), 1)
    return None


def _get_bmi_category(bmi: Optional[float], age: Optional[int]) -> Optional[str]:
    """Return an age-aware BMI category string.
    
    - Children/Teens (<20): BMI percentile-based interpretation is recommended,
      but we provide a general note since full CDC charts are complex.
    - Adults (20-64): Standard WHO categories.
    - Seniors (65+): Slightly adjusted thresholds — a BMI of 23-30 is generally
      considered healthy for older adults.
    """
    if bmi is None:
        return None

    # Children & Teens: flag that standard categories don't fully apply
    if age is not None and age < 20:
        if bmi < 14.0:
            return "Underweight (youth)"
        elif bmi < 22.0:
            return "Normal range (youth — consult BMI-for-age chart)"
        elif bmi < 27.0:
            return "Overweight (youth)"
        else:
            return "Obese (youth)"

    # Seniors (65+): adjusted thresholds
    if age is not None and age >= 65:
        if bmi < 23.0:
            return "Underweight (senior)"
        elif bmi < 30.0:
            return "Normal weight (senior)"
        elif bmi < 35.0:
            return "Overweight (senior)"
        else:
            return "Obese (senior)"

    # Standard adult categories (20-64, or age unknown)
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal weight"
    elif bmi < 30.0:
        return "Overweight"
    else:
        return "Obese"


def _build_prefs_dto(prefs, current_user: User) -> UserPreferencesDto:
    """Build a UserPreferencesDto from a UserPreferences model instance."""
    bmi = _calculate_bmi(prefs.height, prefs.weight)
    age = _calculate_age(current_user.date_of_birth)
    bmi_category = _get_bmi_category(bmi, age)
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
        bmi=bmi,
        bmi_category=bmi_category
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
    
    return _build_prefs_dto(prefs, current_user)

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
    
    return _build_prefs_dto(prefs, current_user)

