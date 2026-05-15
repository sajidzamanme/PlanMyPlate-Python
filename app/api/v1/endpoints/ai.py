"""
AI endpoints — recipe and meal plan generation via Google Gemini.
"""

from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.models.user import User
from app.schemas.ai import AiRecipeRequestDto
from app.schemas.recipe import RecipeResponse
from app.schemas.meal_plan import MealPlanResponse
from app.services.gemini_service import gemini_service

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /ai/generate-recipe
# ---------------------------------------------------------------------------

@router.post("/generate-recipe", response_model=RecipeResponse, status_code=201)
def generate_recipe(
    *,
    db: Session = Depends(deps.get_db),
    request: AiRecipeRequestDto,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Generate a custom recipe using Google Gemini AI.

    The AI returns a full recipe including macronutrients (protein, carbs, fat,
    fiber). The recipe is saved to the database and returned.

    Requires a valid GEMINI_API_KEY in the server's .env file.
    """
    try:
        recipe_dto = gemini_service.generate_recipe(request, db)
    except ValueError as exc:
        # GEMINI_API_KEY not configured
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI recipe generation failed: {str(exc)}",
        )

    # Persist the generated recipe
    saved_recipe = crud.recipe.create_recipe(db, obj_in=recipe_dto)
    return saved_recipe


# ---------------------------------------------------------------------------
# POST /ai/generate-meal-plan
# ---------------------------------------------------------------------------

@router.post("/generate-meal-plan", response_model=MealPlanResponse, status_code=201)
def generate_meal_plan(
    *,
    db: Session = Depends(deps.get_db),
    userId: int = Query(..., description="ID of the user to generate the plan for"),
    startDate: Optional[str] = Query(None, description="Start date (YYYY-MM-DD), defaults to today"),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Generate a complete 7-day meal plan (21 meals) via Google Gemini AI.

    The AI suggests meal names for each slot. Matching recipes are looked up in
    the database; unmatched slots are left without a recipe (null). The plan and
    its grocery list are saved automatically.

    Requires a valid GEMINI_API_KEY in the server's .env file.
    """
    if userId != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Parse start date
    if startDate:
        try:
            plan_start = date.fromisoformat(startDate)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid startDate format. Use YYYY-MM-DD.")
    else:
        plan_start = date.today()

    # Fetch user preferences for personalised prompt
    prefs = crud.user_preferences.get_by_user_id(db, user_id=userId)
    diet = prefs.diet.diet_name if prefs and prefs.diet else None
    allergies = prefs.allergies if prefs and prefs.allergies else []
    dislikes = prefs.dislikes if prefs and prefs.dislikes else []

    allergy_names = [a.name for a in allergies]
    dislike_names = [d.name for d in dislikes]

    try:
        meals = gemini_service.generate_meal_plan_recipe_names(
            diet=diet,
            allergies=allergy_names,
            dislikes=dislike_names,
        )
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI meal plan generation failed: {str(exc)}",
        )

    # Map meal slots to recipe IDs (best-effort name match)
    recipe_ids: list[int] = []
    for meal in meals:
        recipe_name: str = meal.get("recipeName", "")
        matches = crud.recipe.search_by_name(db, name=recipe_name)
        recipe_ids.append(matches[0].recipe_id if matches else None)  # type: ignore[arg-type]

    # Filter out None values for the create call (use only found recipes)
    valid_recipe_ids = [rid for rid in recipe_ids if rid is not None]

    # Use existing CRUD to create the meal plan with recipe slots
    from app.schemas.meal_plan import MealPlanRequestDto
    dto = MealPlanRequestDto(
        recipeIds=valid_recipe_ids,
        duration=7,
        startDate=str(plan_start),
    )
    meal_plan = crud.meal_plan.create_with_recipes(db, user_id=userId, dto=dto)

    # Populate grocery list (mirrors logic from meal_plans endpoint)
    from app.schemas.ingredient import IngredientQuantityDto

    recipe_counts: dict[int, int] = {}
    for rid in valid_recipe_ids:
        recipe_counts[rid] = recipe_counts.get(rid, 0) + 1

    ingredient_dtos = []
    processed: set[int] = set()
    for rid in valid_recipe_ids:
        if rid in processed:
            continue
        processed.add(rid)
        recipe = crud.recipe.get(db, id=rid)
        if not recipe:
            continue
        count = recipe_counts[rid]
        for ri in recipe.recipe_ingredients:
            ingredient_dtos.append(
                IngredientQuantityDto(
                    ingredient=ri.ingredient,
                    quantity=ri.quantity * count if ri.quantity else 0,
                    unit=ri.unit or "unit",
                )
            )

    if ingredient_dtos:
        crud.grocery_list.add_ingredients_with_quantities(
            db, user_id=userId, ingredient_data=ingredient_dtos
        )

    return meal_plan
