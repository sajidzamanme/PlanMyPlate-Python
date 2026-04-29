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
        allergies = [a.allergy_name for a in prefs.allergies] if prefs else []
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
            quantity = ing.get("quantity", 0)
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
