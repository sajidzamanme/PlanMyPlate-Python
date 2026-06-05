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

from google import genai
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.ai import AiRecipeRequestDto
from app.schemas.recipe import RecipeCreateDto, RecipeIngredientDto

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-3.5-flash"


# ---------------------------------------------------------------------------
# Gemini client initialisation
# ---------------------------------------------------------------------------

def _get_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. Add it to your .env file to use AI features."
        )
    return genai.Client(api_key=settings.GEMINI_API_KEY)


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
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    return json.loads(text)


class GeminiAiService:
    def generate_recipe(self, request: AiRecipeRequestDto, db: Session) -> RecipeCreateDto:
        from app import crud
        from app.schemas.ingredient import IngredientCreate

        client = _get_client()
        prompt = _build_recipe_prompt(request)

        logger.info("Sending recipe generation prompt to Gemini...")
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        raw_text = response.text.strip()
        logger.debug("Gemini raw response: %s", raw_text)

        data = _parse_json_from_text(raw_text)

        ingredient_dtos: list[RecipeIngredientDto] = []
        for ing_data in data.get("ingredients", []):
            name: str = ing_data.get("name", "").strip()
            quantity = ing_data.get("quantity", 1)
            unit = ing_data.get("unit", "unit")

            if not name:
                continue

            matches = crud.ingredient.search_by_name(db, name=name)
            if matches:
                ingredient = matches[0]
            else:
                ingredient = crud.ingredient.create(
                    db, obj_in=IngredientCreate(name=name, price=0.0)
                )

            ingredient_dtos.append(
                RecipeIngredientDto(
                    ingId=ingredient.ing_id,
                    quantity=float(quantity),
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
            instructions=data.get("instructions"),
            imageUrl=None,
            ingredients=ingredient_dtos,
        )
        return recipe_dto

    def generate_meal_plan_recipes(
        self,
        user_prefs: dict,
        existing_recipes: list[dict],
    ) -> list[dict]:
        _MEAL_PLAN_JSON_SCHEMA = """{
          "meals": [
            {
              "day": <integer 1-7>,
              "mealType": "<Breakfast | Lunch | Dinner>",
              "recipeId": <integer ID of selected recipe, or null if a new recipe is generated>,
              "recipeName": "<name of the selected or newly created recipe>",
              "newRecipe": <null if recipeId is specified, or a full recipe JSON object matching the RECIPE schema if recipeId is null>
            }
          ]
        }"""

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
          "instructions": "<full step-by-step cooking instructions (string)>",
          "ingredients": [
            {
              "name": "<ingredient name>",
              "quantity": <numeric amount>,
              "unit": "<unit of measurement, e.g. g, ml, cup, tbsp>"
            }
          ]
        }"""

        prefs_str = json.dumps(user_prefs, indent=2)
        recipes_str = json.dumps(existing_recipes, indent=2)

        prompt = f"""You are a professional nutritionist and chef. Create a balanced 7-day meal plan (Breakfast, Lunch, Dinner for each day = 21 meals total) for a user with the following profile:

USER PROFILE:
{prefs_str}

We have a database of existing recipes:
EXISTING RECIPES:
{recipes_str}

YOUR TASK:
For each of the 21 meal slots (7 days × 3 meals: Breakfast, Lunch, Dinner), you must:
1. Try to select an existing recipe from the database that matches the user's dietary preferences, restrictions, and nutritional target. If you select an existing recipe, set "recipeId" to its ID and set "newRecipe" to null.
2. If none of the existing recipes match the requirements or you want to provide variety, you must design a NEW recipe specifically tailored to the user's constraints. If you design a new recipe, set "recipeId" to null, and provide the complete recipe details in the "newRecipe" field (including ingredients, cooking steps, and macronutrients).

OUTPUT RULES:
1. Return ONLY a single valid JSON object — no markdown fences, no extra text.
2. The meals array must have exactly 21 entries (7 days × 3 meal types).
3. Each entry must have: day (1-7), mealType (Breakfast/Lunch/Dinner), recipeId, recipeName, newRecipe.
4. Vary the meals — do not repeat the same recipe on the same day.
5. The JSON must exactly match this schema:

{_MEAL_PLAN_JSON_SCHEMA}

Where the "newRecipe" field schema is:
{_RECIPE_JSON_SCHEMA}
"""
        client = _get_client()

        logger.info("Sending meal plan generation prompt to Gemini...")
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        raw_text = response.text.strip()
        logger.debug("Gemini raw response: %s", raw_text)

        data = _parse_json_from_text(raw_text)
        return data.get("meals", [])


gemini_service = GeminiAiService()
