"""
Gemini AI Service for PlanMyPlate.

Handles:
  - AI recipe generation (with full macronutrient data)
  - AI weekly meal plan generation
"""

import json
import re
import logging
from typing import Optional
from datetime import date

import google.generativeai as genai
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.ai import AiRecipeRequestDto
from app.schemas.recipe import RecipeCreateDto, RecipeIngredientDto

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gemini client initialisation
# ---------------------------------------------------------------------------

def _get_model() -> genai.GenerativeModel:
    """Return a configured Gemini GenerativeModel instance."""
    if not settings.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. Add it to your .env file to use AI features."
        )
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-1.5-flash")


# ---------------------------------------------------------------------------
# Recipe Generation
# ---------------------------------------------------------------------------

_RECIPE_JSON_SCHEMA = """{
  "name": "<recipe name (string)>",
  "description": "<short description (string)>",
  "calories": <integer — total calories per serving>,
  "protein": <float — grams of protein per serving>,
  "carbs": <float — grams of carbohydrates per serving>,
  "fat": <float — grams of fat per serving>,
  "fiber": <float — grams of dietary fiber per serving>,
  "prepTime": <integer — preparation time in minutes>,
  "cookTime": <integer — cooking time in minutes>,
  "servings": <integer — number of servings>,
  "instructions": "<full step-by-step cooking instructions (string)>",
  "ingredients": [
    {
      "name": "<ingredient name>",
      "quantity": <numeric amount>,
      "unit": "<unit of measurement, e.g. g, ml, cup, tbsp>"
    }
  ]
}"""


def _build_recipe_prompt(req: AiRecipeRequestDto) -> str:
    constraints: list[str] = []

    if req.availableIngredients:
        constraints.append(
            f"- Preferred ingredients (use as many as possible): {', '.join(req.availableIngredients)}"
        )
    if req.maxCalories:
        constraints.append(f"- Maximum calories per serving: {req.maxCalories} kcal")
    if req.cuisineType:
        constraints.append(f"- Cuisine type: {req.cuisineType}")
    if req.allergies:
        constraints.append(f"- Avoid allergens: {', '.join(req.allergies)}")
    if req.dietaryPreference:
        constraints.append(f"- Dietary preference: {req.dietaryPreference}")
    if req.mood:
        constraints.append(f"- Mood / occasion: {req.mood}")
    if req.maxCookingTime:
        constraints.append(
            f"- Maximum total cooking time (prep + cook): {req.maxCookingTime} minutes"
        )
    constraints.append(f"- Number of servings: {req.servings}")

    constraint_block = "\n".join(constraints) if constraints else "  (no specific constraints)"

    return f"""You are a professional chef and nutritionist. Your task is to create ONE recipe.

CONSTRAINTS:
{constraint_block}

OUTPUT RULES:
1. Return ONLY a single valid JSON object — no markdown fences, no extra text, no comments.
2. All numeric values must be numbers (not strings).
3. Nutritional values (calories, protein, carbs, fat, fiber) must be realistic and accurate per serving.
4. The JSON must exactly match this schema:

{_RECIPE_JSON_SCHEMA}
"""


def _parse_json_from_text(text: str) -> dict:
    """Extract and parse the first JSON object found in a string."""
    # Strip markdown fences if Gemini wraps despite instructions
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    return json.loads(text)


def generate_recipe(req: AiRecipeRequestDto, db: Session) -> RecipeCreateDto:
    """
    Call Gemini to generate a recipe and return it as a RecipeCreateDto.
    Ingredient matching/creation is handled by the endpoint layer.
    """
    from app import crud  # local import to avoid circular deps

    model = _get_model()
    prompt = _build_recipe_prompt(req)

    logger.info("Sending recipe generation prompt to Gemini...")
    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    logger.debug("Gemini raw response: %s", raw_text)

    data = _parse_json_from_text(raw_text)

    # ------------------------------------------------------------------
    # Map ingredients: look up existing by name (case-insensitive),
    # create if not found.
    # ------------------------------------------------------------------
    ingredient_dtos: list[RecipeIngredientDto] = []
    for ing_data in data.get("ingredients", []):
        name: str = ing_data.get("name", "").strip()
        quantity = ing_data.get("quantity", 1)
        unit = ing_data.get("unit", "unit")

        if not name:
            continue

        # Search existing ingredients
        matches = crud.ingredient.search_by_name(db, name=name)
        if matches:
            ingredient = matches[0]
        else:
            # Create a new ingredient with price 0 (can be updated later)
            from app.schemas.ingredient import IngredientCreate
            ingredient = crud.ingredient.create(
                db, obj_in=IngredientCreate(name=name, price=0.0)
            )

        ingredient_dtos.append(
            RecipeIngredientDto(
                ingId=ingredient.ing_id,
                quantity=int(quantity) if isinstance(quantity, float) and quantity == int(quantity) else quantity,
                unit=str(unit),
            )
        )

    recipe_dto = RecipeCreateDto(
        name=data.get("name", "AI Generated Recipe"),
        description=data.get("description"),
        calories=data.get("calories"),
        protein=data.get("protein"),
        carbs=data.get("carbs"),
        fat=data.get("fat"),
        fiber=data.get("fiber"),
        prepTime=data.get("prepTime"),
        cookTime=data.get("cookTime"),
        servings=data.get("servings", req.servings),
        instructions=data.get("instructions"),
        imageUrl=None,
        ingredients=ingredient_dtos,
    )
    return recipe_dto


# ---------------------------------------------------------------------------
# Meal Plan Generation
# ---------------------------------------------------------------------------

_MEAL_PLAN_JSON_SCHEMA = """{
  "meals": [
    {
      "day": <integer 1-7>,
      "mealType": "<Breakfast | Lunch | Dinner>",
      "recipeName": "<name of the recipe>"
    }
  ]
}"""


def _build_meal_plan_prompt(
    diet: Optional[str],
    allergies: list[str],
    dislikes: list[str],
    servings: int,
) -> str:
    constraints: list[str] = []
    if diet:
        constraints.append(f"- Dietary preference: {diet}")
    if allergies:
        constraints.append(f"- Avoid allergens: {', '.join(allergies)}")
    if dislikes:
        constraints.append(f"- Disliked ingredients (avoid): {', '.join(dislikes)}")
    constraints.append(f"- Servings per meal: {servings}")
    constraint_block = "\n".join(constraints) if constraints else "  (no specific constraints)"

    return f"""You are a professional nutritionist. Create a balanced 7-day meal plan (Breakfast, Lunch, Dinner for each day = 21 meals total).

CONSTRAINTS:
{constraint_block}

OUTPUT RULES:
1. Return ONLY a single valid JSON object — no markdown fences, no extra text.
2. The meals array must have exactly 21 entries (7 days × 3 meal types).
3. Each entry must have: day (1-7), mealType (Breakfast/Lunch/Dinner), recipeName.
4. Vary the meals — do not repeat the same recipe on the same day.
5. The JSON must exactly match this schema:

{_MEAL_PLAN_JSON_SCHEMA}
"""


def generate_meal_plan_recipe_names(
    diet: Optional[str],
    allergies: list[str],
    dislikes: list[str],
    servings: int,
) -> list[dict]:
    """
    Call Gemini to generate a 7-day meal plan.
    Returns a list of dicts: [{day, mealType, recipeName}, ...]
    """
    model = _get_model()
    prompt = _build_meal_plan_prompt(diet, allergies, dislikes, servings)

    logger.info("Sending meal plan generation prompt to Gemini...")
    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    logger.debug("Gemini raw response: %s", raw_text)

    data = _parse_json_from_text(raw_text)
    return data.get("meals", [])
