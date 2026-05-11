from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.schemas.user import UserDto, UserUpdate, UserPreferencesDto
from app.models.user import User

router = APIRouter()

@router.get("/me", response_model=UserDto)
def read_user_me(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    return UserDto(
        userId=current_user.user_id,
        email=current_user.email,
        firstName=current_user.first_name,
        lastName=current_user.last_name,
        phone=current_user.phone,
        dateOfBirth=current_user.date_of_birth
    )

@router.put("/{user_id}", response_model=UserDto)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    # Authorization check (can user update another user?)
    # Java code doesn't explicitly forbid, but implies self-update usually.
    # Assuming user can only update themselves or admin (no admin role yet).
    if user.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return UserDto(
        userId=user.user_id,
        email=user.email,
        firstName=user.first_name,
        lastName=user.last_name,
        phone=user.phone,
        dateOfBirth=user.date_of_birth
    )

@router.delete("/{user_id}")
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    if user.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    crud.user.remove(db, id=user_id)
    return {"message": "User deleted successfully"}
