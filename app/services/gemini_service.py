<<<<<<< HEAD
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
=======
import json
import requests
from typing import List, Any, Optional
from sqlalchemy.orm import Session
from datetime import date

from app import crud
from app.core.config import settings
from app.schemas.ai import AiRecipeRequestDto
from app.models.recipe import Recipe, RecipeIngredient
from app.models.meal_plan import MealPlan, MealSlot
from app.schemas.recipe import RecipeCreateDto, RecipeIngredientDto
from app.schemas.meal_plan import MealPlanRequestDto

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

class GeminiAiService:
    def call_gemini_api(self, prompt: str) -> str:
        if not settings.GEMINI_API_KEY:
            raise Exception("Gemini API Key not configured")
            
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        response = requests.post(
            f"{GEMINI_API_URL}?key={settings.GEMINI_API_KEY}",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        
        result = response.json()
        try:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise Exception("Unexpected response from Gemini API")

    def extract_json(self, text: str) -> str:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]
        return text

    def generate_recipe(self, db: Session, request: AiRecipeRequestDto) -> Recipe:
        # Build prompt (simplified from Java logic, but should match essence)
        prompt = self.build_recipe_prompt(db, request)
        ai_response = self.call_gemini_api(prompt)
        json_str = self.extract_json(ai_response)
        
        data = json.loads(json_str)
        
        # Parse and save
        return self.parse_and_save_recipe(db, data)

    def generate_weekly_meal_plan(self, db: Session, user_id: int, start_date: Optional[date] = None) -> MealPlan:
        # Fetch user prefs
        prefs = crud.user_preferences.get_by_user_id(db, user_id=user_id)
        
        # We need 7 breakfasts, 7 lunches, 7 dinners.
        meal_types = ["Breakfast", "Lunch", "Dinner"]
        generated_recipe_ids = []
        
        for meal_type in meal_types:
            prompt = self.build_weekly_prompt(db, prefs, meal_type)
            ai_response = self.call_gemini_api(prompt)
            json_str = self.extract_json(ai_response)
            data = json.loads(json_str)
            
            recipes_data = data.get("recipes", [])
            for r_data in recipes_data:
                recipe = self.parse_and_save_recipe(db, r_data)
                generated_recipe_ids.append(recipe.recipe_id)
        
        # Reorder: AI returns B1..B7, L1..L7, D1..D7
        # create_with_recipes expects: B1, L1, D1, B2, L2, D2...
        ordered_ids = []
        for i in range(7):
            if i < len(generated_recipe_ids):
                ordered_ids.append(generated_recipe_ids[i])
            if i + 7 < len(generated_recipe_ids):
                ordered_ids.append(generated_recipe_ids[i + 7])
            if i + 14 < len(generated_recipe_ids):
                ordered_ids.append(generated_recipe_ids[i + 14])
                
        dto = MealPlanRequestDto(
            recipeIds=ordered_ids,
            servingsMultipliers=[1] * len(ordered_ids),
            duration=7,
            startDate=start_date or date.today()
        )
        return crud.meal_plan.create_with_recipes(db, user_id=user_id, dto=dto)

    def get_database_summary(self, db: Session) -> str:
        recipes = crud.recipe.get_multi(db, limit=100)
        summary = "Existing Recipes in Database:\n"
        for r in recipes:
            ing_names = [ri.ingredient.name for ri in r.recipe_ingredients]
            summary += f"- ID: {r.recipe_id}, Name: {r.name}, Ingredients: {', '.join(ing_names)}\n"
        return summary

    def build_recipe_prompt(self, db: Session, request: AiRecipeRequestDto) -> str:
        db_summary = self.get_database_summary(db)
        return f"""
        You are a professional chef. Generate a detailed recipe.
        {db_summary}
        IMPORTANT: Before creating new, check if one above matches. If so, reuse it by setting isNew: false and providing recipeId.
        
        Requirements:
        Available Ingredients: {', '.join(request.availableIngredients)}
        Max Calories: {request.maxCalories}
        Cuisine: {request.cuisineType}
        Allergies: {', '.join(request.allergies)}
        Diet: {request.dietaryPreference}
        Mood: {request.mood}
        Servings: {request.servings}
        
        Provide JSON format ONLY:
        {{
          "isNew": true,
          "recipeId": null,
          "name": "Recipe Name",
          "description": "...",
          "calories": 400,
          "prepTime": 10,
          "cookTime": 20,
          "servings": {request.servings},
          "instructions": "...",
          "imageUrl": "...",
          "ingredients": [ {{"name": "...", "quantity": 100, "unit": "g"}} ]
        }}
        """

    def build_weekly_prompt(self, db: Session, prefs, meal_type: str) -> str:
        db_summary = self.get_database_summary(db)
        diet = prefs.diet.diet_name if prefs and prefs.diet else "None"
        allergies = [a.name for a in prefs.allergies] if prefs else []
        return f"""
        Generate 7 DISTINCT {meal_type} recipes for a weekly meal plan.
        {db_summary}
        IMPORTANT: Prefer reusing 'Existing Recipes' from the list above if they fit.
        
        Diet: {diet}
        Allergies: {', '.join(allergies)}
        
        Provide JSON format ONLY:
        {{
          "recipes": [
            {{
              "isNew": true,
              "recipeId": null,
              "name": "Recipe Name",
              "description": "...",
              "calories": 400,
              "prepTime": 10,
              "cookTime": 20,
              "servings": 2,
              "instructions": "...",
              "imageUrl": "...",
              "ingredients": [ {{"name": "...", "quantity": 100, "unit": "g"}} ]
            }}
          ]
        }}
        """

    def parse_and_save_recipe(self, db: Session, data: dict) -> Recipe:
        is_new = data.get("isNew", True)
        recipe_id = data.get("recipeId")
        
        if not is_new and recipe_id:
            recipe = crud.recipe.get(db, id=recipe_id)
            if recipe: return recipe
            
        # Create new
        ingredients_data = data.get("ingredients", [])
        recipe_ingredients = []
        
        for ing in ingredients_data:
            name = ing.get("name", "Unknown")
            # Convert quantity to float to support fractional amounts (0.5, 1.5, etc.)
            try:
                quantity = float(ing.get("quantity", 0))
            except (ValueError, TypeError):
                quantity = 0.0
            unit = ing.get("unit", "unit")
            
            # Find/Create ingredient
            ingredient = crud.ingredient.get_by_name(db, name=name)
            if not ingredient:
                from app.schemas.ingredient import IngredientCreate
                ingredient = crud.ingredient.create(db, obj_in=IngredientCreate(name=name))
            
            recipe_ingredients.append(RecipeIngredientDto(
                ingId=ingredient.ing_id,
                quantity=quantity,
                unit=unit
            ))
            
        create_dto = RecipeCreateDto(
            name=data.get("name", "Unknown"),
            description=data.get("description"),
            calories=data.get("calories"),
            prepTime=data.get("prepTime"),
            cookTime=data.get("cookTime"),
            servings=data.get("servings"),
            instructions=data.get("instructions"),
            imageUrl=data.get("imageUrl"),
            ingredients=recipe_ingredients
        )
        return crud.recipe.create_recipe(db, obj_in=create_dto)

gemini_service = GeminiAiService()
>>>>>>> 8bfbfb597cfd63ddae450134a8d51ecded8fee4b
