from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.schemas.meal_plan import MealPlanResponse, MealPlanCreate, MealPlanUpdate, MealPlanRequestDto
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

@router.post("/user/{user_id}", response_model=MealPlanResponse, status_code=201)
def create_meal_plan(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    meal_plan_in: MealPlanCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return crud.meal_plan.create_simple(db, user_id=user_id, obj_in=meal_plan_in)

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
    
    # Logic to populate grocery list
    # Aggregate ingredients
    ingredient_map = {}
    
    # Need to access meal_plan slots and their recipes
    # Assuming crud_meal_plan loaded them eagerly or lazy loading works in same session
    
    # Re-fetch meal_plan to ensure relationships loaded if needed
    # Or rely on session cache
    
    recipe_ids = dto.recipeIds
    # ... Wait, replicating logic from Java service where it aggregates ingredients
    # I should probably move this logic to CRUD or a service layer.
    # But CRUD `create_with_recipes` already created slots.
    
    # Let's do it here or in CRUD.
    # Java does: createWithRecipes -> calls groceryListService.addIngredientsWithQuantities
    # I can call crud.grocery_list.add_ingredients_with_quantities here.
    
    # But I need the recipe ingredients.
    # I can fetch recipes and aggregate.
    
    from app.schemas.ingredient import IngredientQuantityDto
    
    # Count recipe occurrences
    recipe_counts = {}
    for rid in recipe_ids:
        recipe_counts[rid] = recipe_counts.get(rid, 0) + 1
    
    ingredient_dtos = []
    
    # Fetch recipes
    # Optimization: fetch all unique recipes in one query?
    # crud.recipe.get_multi would need filtering by IDs.
    # Simple loop for now.
    
    processed_recipes = set()
    for rid in recipe_ids:
        if rid in processed_recipes: continue
        processed_recipes.add(rid)
        
        recipe = crud.recipe.get(db, id=rid)
        if not recipe: continue
        
        count = recipe_counts[rid]
        
        for ri in recipe.recipe_ingredients:
            # Map to DTO
            dto = IngredientQuantityDto(
                ingredient=ri.ingredient,
                quantity=ri.quantity * count if ri.quantity else 0,
                unit=ri.unit or "unit"
            )
            ingredient_dtos.append(dto)
            
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
