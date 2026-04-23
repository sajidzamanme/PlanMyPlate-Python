from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.schemas.user import UserPreferencesDto
from app.models.user import User

router = APIRouter()

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
        return UserPreferencesDto(userId=user_id, servings=1, allergies=[], dislikes=[])
    
    # Map entity to DTO (SQLAlchemy models usually can be converted via from_attributes in Pydantic, 
    # but for nested lists of strings we might need manual mapping if Pydantic doesn't handle it perfectly directly 
    # with the provided structure. Let's see if Pydantic magic works.
    # The Pydantic model expects list of strings for allergies/dislikes.
    # The SQLAlchemy model has list of Allergy/Ingredient objects.
    # We might need a custom mapping or property on the model.
    # For simplicity, I'll construct it manually here.)
    
    return UserPreferencesDto(
        prefId=prefs.pref_id,
        userId=prefs.user_id,
        diet=prefs.diet.diet_name if prefs.diet else None,
        allergies=[a.allergy_name for a in prefs.allergies],
        dislikes=[d.name for d in prefs.dislikes],
        servings=prefs.servings,
        budget=prefs.budget
    )

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
    
    return UserPreferencesDto(
        prefId=prefs.pref_id,
        userId=prefs.user_id,
        diet=prefs.diet.diet_name if prefs.diet else None,
        allergies=[a.allergy_name for a in prefs.allergies],
        dislikes=[d.name for d in prefs.dislikes],
        servings=prefs.servings,
        budget=prefs.budget
    )
