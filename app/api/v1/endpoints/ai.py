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
        raise HTTPException(status_code=503, detail="Gemini API is not configured on the server. Please check environment settings.")
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="AI recipe generation failed. Please try again later.",
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
    
    # Calculate age and BMI
    from app.api.v1.endpoints.user_preferences import _calculate_bmi, _get_bmi_category, _calculate_age
    age = _calculate_age(current_user.date_of_birth) or current_user.age
    
    height = prefs.height if prefs else None
    weight = prefs.weight if prefs else None
    gender = prefs.gender if prefs else None
    budget = prefs.budget if prefs else None
    diets = [d.diet_name for d in prefs.diets] if prefs and prefs.diets else []
    allergies = [a.name for a in prefs.allergies] if prefs and prefs.allergies else []
    dislikes = [d.name for d in prefs.dislikes] if prefs and prefs.dislikes else []
    
    bmi = _calculate_bmi(height, weight)
    bmi_category = _get_bmi_category(bmi, age)
    
    user_prefs_data = {
        "age": age,
        "gender": gender,
        "height": float(height) if height else None,
        "weight": float(weight) if weight else None,
        "bmi": bmi,
        "bmi_category": bmi_category,
        "budget": float(budget) if budget else None,
        "diet": ", ".join(diets) if diets else None,
        "diets": diets,
        "allergies": allergies,
        "dislikes": dislikes
    }

    # Fetch existing recipes
    from app.models.recipe import Recipe
    db_recipes = db.query(Recipe).all()
    recipes_data = []
    for r in db_recipes:
        ingredients = []
        for ri in r.recipe_ingredients:
            ingredients.append({
                "name": ri.ingredient.name,
                "quantity": ri.quantity,
                "unit": ri.unit
            })
        recipes_data.append({
            "recipeId": r.recipe_id,
            "name": r.name,
            "description": r.description,
            "calories": r.calories,
            "protein": r.protein,
            "carbs": r.carbs,
            "fat": r.fat,
            "fiber": r.fiber,
            "prepTime": r.prep_time,
            "cookTime": r.cook_time,
            "ingredients": ingredients
        })

    try:
        meals = gemini_service.generate_meal_plan_recipes(
            user_prefs=user_prefs_data,
            existing_recipes=recipes_data,
        )
    except ValueError as exc:
        raise HTTPException(status_code=503, detail="Gemini API is not configured on the server. Please check environment settings.")
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="AI meal plan generation failed. Please try again later.",
        )

    # Sort the meals by day and mealType to ensure correct slot ordering
    meal_type_order = {"Breakfast": 0, "Lunch": 1, "Dinner": 2}
    sorted_meals = sorted(
        meals,
        key=lambda m: (int(m.get("day", 1)), meal_type_order.get(m.get("mealType", "Breakfast"), 0))
    )

    # Map meal slots to recipe IDs (validate or create)
    from app.schemas.recipe import RecipeCreateDto, RecipeIngredientDto
    from app.schemas.ingredient import IngredientCreate

    recipe_ids: list[int] = []
    for meal in sorted_meals:
        recipe_id = meal.get("recipeId")
        recipe_name = meal.get("recipeName", "")
        new_recipe_details = meal.get("newRecipe")

        db_recipe = None
        if recipe_id is not None:
            db_recipe = crud.recipe.get(db, id=recipe_id)

        # Fallback to search by name if ID was not found/invalid
        if not db_recipe and recipe_name:
            matches = crud.recipe.search_by_name(db, name=recipe_name)
            if matches:
                db_recipe = matches[0]

        # If still not found, we create a new recipe
        if not db_recipe:
            if new_recipe_details and isinstance(new_recipe_details, dict):
                recipe_data = new_recipe_details
            else:
                recipe_data = {"name": recipe_name or "AI Generated Recipe"}

            ingredient_dtos = []
            for ing_data in recipe_data.get("ingredients", []):
                ing_name = ing_data.get("name", "").strip()
                quantity = ing_data.get("quantity", 1)
                unit = ing_data.get("unit", "unit")
                if not ing_name:
                    continue

                matches = crud.ingredient.search_by_name(db, name=ing_name)
                if matches:
                    ingredient = matches[0]
                else:
                    ingredient = crud.ingredient.create(
                        db, obj_in=IngredientCreate(name=ing_name, price=0.0)
                    )

                ingredient_dtos.append(
                    RecipeIngredientDto(
                        ingId=ingredient.ing_id,
                        quantity=float(quantity),
                        unit=str(unit),
                    )
                )

            recipe_dto = RecipeCreateDto(
                name=recipe_data.get("name", recipe_name or "AI Generated Recipe"),
                description=recipe_data.get("description"),
                calories=recipe_data.get("calories"),
                protein=recipe_data.get("protein"),
                carbs=recipe_data.get("carbs"),
                fat=recipe_data.get("fat"),
                fiber=recipe_data.get("fiber"),
                prepTime=recipe_data.get("prepTime") or recipe_data.get("prep_time"),
                cookTime=recipe_data.get("cookTime") or recipe_data.get("cook_time"),
                instructions=recipe_data.get("instructions"),
                imageUrl=None,
                ingredients=ingredient_dtos,
            )
            db_recipe = crud.recipe.create_recipe(db, obj_in=recipe_dto)

        recipe_ids.append(db_recipe.recipe_id)

    # Use existing CRUD to create the meal plan with recipe slots
    from app.schemas.meal_plan import MealPlanRequestDto
    dto = MealPlanRequestDto(
        recipeIds=recipe_ids,
        duration=7,
        startDate=str(plan_start),
    )
    meal_plan = crud.meal_plan.create_with_recipes(db, user_id=userId, dto=dto)

    # Populate grocery list (mirrors logic from meal_plans endpoint)
    from app.schemas.ingredient import IngredientQuantityDto

    recipe_counts: dict[int, int] = {}
    for rid in recipe_ids:
        recipe_counts[rid] = recipe_counts.get(rid, 0) + 1

    ingredient_dtos = []
    processed: set[int] = set()
    for rid in recipe_ids:
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
