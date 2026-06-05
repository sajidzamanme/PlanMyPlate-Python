import pytest
from unittest.mock import MagicMock
from datetime import date

from app.services.gemini_service import gemini_service
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreateDto, RecipeIngredientDto

def _create_test_recipe(db_session, name: str) -> Recipe:
    """Insert a recipe directly into the DB and return it."""
    recipe = Recipe(
        name=name,
        description="Test description",
        calories=300,
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    return recipe

class TestAiEndpoints:
    def test_generate_recipe_success(self, client, auth_headers):
        # Mock generate_recipe on gemini_service
        original_generate_recipe = gemini_service.generate_recipe
        mock_dto = RecipeCreateDto(
            name="Mocked Pizza",
            description="Tasty pizza",
            calories=400,
            protein=20.0,
            carbs=50.0,
            fat=15.0,
            fiber=5.0,
            prepTime=15,
            cookTime=15,
            instructions="Bake it.",
            imageUrl=None,
            ingredients=[]
        )
        gemini_service.generate_recipe = MagicMock(return_value=mock_dto)

        try:
            payload = {
                "availableIngredients": ["dough", "cheese", "tomato"],
                "maxCalories": 500,
                "cuisineType": "Italian"
            }
            resp = client.post("/api/ai/generate-recipe", json=payload, headers=auth_headers)
            assert resp.status_code == 201
            data = resp.json()
            assert data["name"] == "Mocked Pizza"
            assert data["calories"] == 400
            assert data["recipeId"] is not None
        finally:
            gemini_service.generate_recipe = original_generate_recipe

    def test_generate_meal_plan_success(self, client, db_session, test_user, auth_headers):
        # Create an existing recipe in the DB
        existing_recipe = _create_test_recipe(db_session, "Classic Salad")

        # Mock generate_meal_plan_recipes on gemini_service
        original_generate_meal_plan_recipes = gemini_service.generate_meal_plan_recipes
        
        # We need 21 meals
        mock_meals = []
        meal_types = ["Breakfast", "Lunch", "Dinner"]
        for day in range(1, 8):
            for meal_type in meal_types:
                if day == 1 and meal_type == "Breakfast":
                    # Use existing recipe
                    mock_meals.append({
                        "day": day,
                        "mealType": meal_type,
                        "recipeId": existing_recipe.recipe_id,
                        "recipeName": existing_recipe.name,
                        "newRecipe": None
                    })
                elif day == 1 and meal_type == "Lunch":
                    # Create a new recipe
                    mock_meals.append({
                        "day": day,
                        "mealType": meal_type,
                        "recipeId": None,
                        "recipeName": "AI Created Pasta",
                        "newRecipe": {
                            "name": "AI Created Pasta",
                            "description": "Tasty custom pasta",
                            "calories": 450,
                            "protein": 15.0,
                            "carbs": 60.0,
                            "fat": 10.0,
                            "fiber": 4.0,
                            "prepTime": 10,
                            "cookTime": 15,
                            "instructions": "Boil pasta and add sauce.",
                            "ingredients": [
                                {"name": "Pasta Noodles", "quantity": 100, "unit": "g"}
                            ]
                        }
                    })
                else:
                    # Default fallback to existing recipe for simplicity
                    mock_meals.append({
                        "day": day,
                        "mealType": meal_type,
                        "recipeId": existing_recipe.recipe_id,
                        "recipeName": existing_recipe.name,
                        "newRecipe": None
                    })

        gemini_service.generate_meal_plan_recipes = MagicMock(return_value=mock_meals)

        try:
            resp = client.post(
                f"/api/ai/generate-meal-plan?userId={test_user.user_id}",
                headers=auth_headers
            )
            assert resp.status_code == 201
            data = resp.json()
            assert data["userId"] == test_user.user_id
            assert data["duration"] == 7
            assert len(data["slots"]) == 21

            # Check that the second slot (Lunch of Day 1) contains the newly created recipe
            slots = data["slots"]
            # Sorting slots by slot index to inspect
            slots.sort(key=lambda s: s["slotIndex"])
            
            # Slot index 0: Breakfast Day 1 (Classic Salad)
            assert slots[0]["recipe"]["recipeId"] == existing_recipe.recipe_id
            assert slots[0]["mealType"] == "Breakfast"
            assert slots[0]["dayNumber"] == 1
            
            # Slot index 1: Lunch Day 1 (AI Created Pasta)
            assert slots[1]["recipe"]["name"] == "AI Created Pasta"
            assert slots[1]["recipe"]["calories"] == 450
            assert slots[1]["mealType"] == "Lunch"
            assert slots[1]["dayNumber"] == 1

            # Ensure the newly created recipe is saved in the database
            db_recipe = db_session.query(Recipe).filter(Recipe.name == "AI Created Pasta").first()
            assert db_recipe is not None
            assert len(db_recipe.recipe_ingredients) == 1
            assert db_recipe.recipe_ingredients[0].ingredient.name == "Pasta Noodles"

        finally:
            gemini_service.generate_meal_plan_recipes = original_generate_meal_plan_recipes
