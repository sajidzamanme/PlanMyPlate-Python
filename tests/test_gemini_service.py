"""
Unit tests for the Gemini AI service.

These tests mock external API calls — no real Gemini key is needed.
We use lazy imports to avoid ImportError when google-genai is not installed.
"""

import pytest
import json
import importlib
import sys


def _can_import_gemini_service() -> bool:
    """Check if the gemini_service module can be imported."""
    try:
        import app.services.gemini_service  # noqa: F401
        return True
    except ImportError:
        return False


# Conditionally skip entire module if google-genai is unavailable
pytestmark = pytest.mark.skipif(
    not _can_import_gemini_service(),
    reason="google-genai is not installed — skipping Gemini service tests",
)


@pytest.fixture()
def gemini_funcs():
    """Lazily import the functions under test."""
    from app.services.gemini_service import _parse_json_from_text, _build_recipe_prompt
    return _parse_json_from_text, _build_recipe_prompt


@pytest.fixture()
def AiRecipeRequestDto_cls():
    from app.schemas.ai import AiRecipeRequestDto
    return AiRecipeRequestDto


class TestParseJsonFromText:
    """Tests for extracting JSON from Gemini's raw response text."""

    def test_clean_json(self, gemini_funcs):
        _parse_json_from_text, _ = gemini_funcs
        raw = '{"name": "Pasta", "calories": 400}'
        result = _parse_json_from_text(raw)
        assert result["name"] == "Pasta"
        assert result["calories"] == 400

    def test_markdown_fenced_json(self, gemini_funcs):
        _parse_json_from_text, _ = gemini_funcs
        raw = '```json\n{"name": "Salad", "calories": 200}\n```'
        result = _parse_json_from_text(raw)
        assert result["name"] == "Salad"
        assert result["calories"] == 200

    def test_markdown_fence_no_lang(self, gemini_funcs):
        _parse_json_from_text, _ = gemini_funcs
        raw = '```\n{"name": "Soup"}\n```'
        result = _parse_json_from_text(raw)
        assert result["name"] == "Soup"

    def test_invalid_json_raises(self, gemini_funcs):
        _parse_json_from_text, _ = gemini_funcs
        with pytest.raises(json.JSONDecodeError):
            _parse_json_from_text("not json at all")


class TestBuildRecipePrompt:
    """Tests for recipe prompt construction."""

    def test_prompt_includes_ingredients(self, gemini_funcs, AiRecipeRequestDto_cls):
        _, _build_recipe_prompt = gemini_funcs
        req = AiRecipeRequestDto_cls(availableIngredients=["chicken", "rice", "garlic"])
        prompt = _build_recipe_prompt(req)
        assert "chicken" in prompt
        assert "rice" in prompt
        assert "garlic" in prompt

    def test_prompt_includes_max_calories(self, gemini_funcs, AiRecipeRequestDto_cls):
        _, _build_recipe_prompt = gemini_funcs
        req = AiRecipeRequestDto_cls(maxCalories=500)
        prompt = _build_recipe_prompt(req)
        assert "500" in prompt
        assert "calories" in prompt.lower()

    def test_prompt_includes_cuisine_type(self, gemini_funcs, AiRecipeRequestDto_cls):
        _, _build_recipe_prompt = gemini_funcs
        req = AiRecipeRequestDto_cls(cuisineType="Italian")
        prompt = _build_recipe_prompt(req)
        assert "Italian" in prompt

    def test_prompt_includes_allergies(self, gemini_funcs, AiRecipeRequestDto_cls):
        _, _build_recipe_prompt = gemini_funcs
        req = AiRecipeRequestDto_cls(allergies=["peanuts", "shellfish"])
        prompt = _build_recipe_prompt(req)
        assert "peanuts" in prompt
        assert "shellfish" in prompt

    def test_prompt_includes_dietary_preference(self, gemini_funcs, AiRecipeRequestDto_cls):
        _, _build_recipe_prompt = gemini_funcs
        req = AiRecipeRequestDto_cls(dietaryPreference="Vegan")
        prompt = _build_recipe_prompt(req)
        assert "Vegan" in prompt

    def test_prompt_includes_mood(self, gemini_funcs, AiRecipeRequestDto_cls):
        _, _build_recipe_prompt = gemini_funcs
        req = AiRecipeRequestDto_cls(mood="comfort food")
        prompt = _build_recipe_prompt(req)
        assert "comfort food" in prompt

    def test_prompt_includes_max_cooking_time(self, gemini_funcs, AiRecipeRequestDto_cls):
        _, _build_recipe_prompt = gemini_funcs
        req = AiRecipeRequestDto_cls(maxCookingTime=30)
        prompt = _build_recipe_prompt(req)
        assert "30" in prompt

    def test_prompt_no_constraints(self, gemini_funcs, AiRecipeRequestDto_cls):
        _, _build_recipe_prompt = gemini_funcs
        req = AiRecipeRequestDto_cls()
        prompt = _build_recipe_prompt(req)
        assert "no specific constraints" in prompt
