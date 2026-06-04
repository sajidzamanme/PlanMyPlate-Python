"""
Unit tests for CRUDRecipe operations.

Uses the SQLite in-memory database from conftest fixtures.
"""

import pytest

from app.crud.crud_recipe import CRUDRecipe
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreateDto


crud_recipe = CRUDRecipe(Recipe)


def _make_recipe_dto(**overrides) -> RecipeCreateDto:
    base = {
        "name": "Test Recipe",
        "description": "A tasty test recipe",
        "calories": 350,
        "protein": 20.0,
        "carbs": 40.0,
        "fat": 10.0,
        "fiber": 5.0,
        "prepTime": 15,
        "cookTime": 30,
        "instructions": "Mix and cook.",
    }
    base.update(overrides)
    return RecipeCreateDto(**base)


class TestCRUDRecipeCreate:
    """Recipe creation via CRUD layer."""

    def test_create_recipe_basic(self, db_session):
        dto = _make_recipe_dto()
        recipe = crud_recipe.create_recipe(db_session, obj_in=dto)

        assert recipe.recipe_id is not None
        assert recipe.name == "Test Recipe"
        assert recipe.calories == 350
        assert recipe.prep_time == 15
        assert recipe.cook_time == 30

    def test_create_recipe_minimal_fields(self, db_session):
        dto = RecipeCreateDto(name="Minimal Recipe")
        recipe = crud_recipe.create_recipe(db_session, obj_in=dto)

        assert recipe.recipe_id is not None
        assert recipe.name == "Minimal Recipe"
        assert recipe.calories is None


class TestCRUDRecipeSearch:
    """Recipe search and filter operations."""

    def _seed_recipes(self, db_session):
        """Insert a few recipes for search/filter tests."""
        for name, cals in [
            ("Chicken Curry", 450),
            ("Chicken Salad", 200),
            ("Pasta Carbonara", 600),
            ("Veggie Stir Fry", 300),
        ]:
            dto = _make_recipe_dto(name=name, calories=cals)
            crud_recipe.create_recipe(db_session, obj_in=dto)

    def test_search_by_name_matching(self, db_session):
        self._seed_recipes(db_session)
        results = crud_recipe.search_by_name(db_session, name="Chicken")
        assert len(results) == 2
        names = {r.name for r in results}
        assert "Chicken Curry" in names
        assert "Chicken Salad" in names

    def test_search_by_name_no_match(self, db_session):
        self._seed_recipes(db_session)
        results = crud_recipe.search_by_name(db_session, name="Sushi")
        assert len(results) == 0

    def test_filter_by_calories_in_range(self, db_session):
        self._seed_recipes(db_session)
        results = crud_recipe.filter_by_calories(db_session, min_cals=200, max_cals=400)
        assert len(results) == 2  # Chicken Salad (200) + Veggie Stir Fry (300)

    def test_filter_by_calories_out_of_range(self, db_session):
        self._seed_recipes(db_session)
        results = crud_recipe.filter_by_calories(db_session, min_cals=700, max_cals=1000)
        assert len(results) == 0
