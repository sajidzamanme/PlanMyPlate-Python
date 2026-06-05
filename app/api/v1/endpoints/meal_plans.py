from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.schemas.meal_plan import MealPlanResponse, MealPlanUpdate, MealPlanRequestDto
from app.models.user import User

router = APIRouter()

@router.get("/user/{user_id}", response_model=List[MealPlanResponse])
def get_user_meal_plans(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return crud.meal_plan.get_by_user_id(db, user_id=user_id)

@router.get("/{id}", response_model=MealPlanResponse)
def get_meal_plan(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    meal_plan = crud.meal_plan.get(db, id=id)
    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    if meal_plan.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return meal_plan

@router.post("/user/{user_id}/create", response_model=MealPlanResponse, status_code=201)
def create_meal_plan_with_recipes(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    dto: MealPlanRequestDto,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    meal_plan = crud.meal_plan.create_with_recipes(db, user_id=user_id, dto=dto)
    
    # Populate grocery list using per-slot serving multipliers
    from app.schemas.ingredient import IngredientQuantityDto
    
    recipe_ids = dto.recipeIds
    multipliers = dto.servingsMultipliers or [1] * len(recipe_ids)
    
    ingredient_dtos = []
    
    for i, rid in enumerate(recipe_ids):
        if i >= 21: break
        
        recipe = crud.recipe.get(db, id=rid)
        if not recipe: continue
        
        multiplier = multipliers[i] if i < len(multipliers) else 1
        
        for ri in recipe.recipe_ingredients:
            ing_dto = IngredientQuantityDto(
                ingredient=ri.ingredient,
                quantity=ri.quantity * multiplier if ri.quantity else 0,
                unit=ri.unit or "unit"
            )
            ingredient_dtos.append(ing_dto)
            
    crud.grocery_list.add_ingredients_with_quantities(db, user_id=user_id, ingredient_data=ingredient_dtos)
    
    return meal_plan

@router.put("/{id}", response_model=MealPlanResponse)
def update_meal_plan(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    meal_plan_in: MealPlanUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    meal_plan = crud.meal_plan.get(db, id=id)
    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    if meal_plan.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return crud.meal_plan.update(db, db_obj=meal_plan, obj_in=meal_plan_in)

@router.delete("/{id}")
def delete_meal_plan(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    meal_plan = crud.meal_plan.get(db, id=id)
    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    if meal_plan.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    crud.meal_plan.remove(db, id=id)
    return {"message": "Meal plan deleted successfully"}

@router.get("/user/{user_id}/status/{status}", response_model=List[MealPlanResponse])
def get_meal_plans_by_status(
    user_id: int,
    status: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return crud.meal_plan.get_by_user_id_and_status(db, user_id=user_id, status=status)

@router.get("/user/{user_id}/weekly", response_model=List[MealPlanResponse])
def get_weekly_meal_plans(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return crud.meal_plan.get_weekly_plans(db, user_id=user_id)

@router.post("/slots/{slot_id}/cook")
def cook_meal_slot(
    *,
    db: Session = Depends(deps.get_db),
    slot_id: int,
    force: bool = False,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    from app.models.meal_plan import MealSlot
    slot = db.query(MealSlot).filter(MealSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Meal slot not found")
        
    if slot.meal_plan.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
        
    servings = float(slot.servings_multiplier)
    
    if not force:
        missing = crud.inventory.check_recipe_ingredients(db, user_id=current_user.user_id, recipe_id=slot.recipe_id, servings=servings)
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
            
    success = crud.inventory.deduct_recipe_ingredients(db, user_id=current_user.user_id, recipe_id=slot.recipe_id, servings=servings)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to cook recipe from slot. Please check your inventory.")
    return {"message": "Meal slot cooked and ingredients deducted from inventory"}

