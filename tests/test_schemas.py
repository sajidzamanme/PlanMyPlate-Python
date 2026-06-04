"""
Unit tests for Pydantic schema validation.

Tests cover: SignUpRequest, UserCreate, RecipeCreateDto, RateRecipeRequest.
"""

import pytest
from datetime import date, timedelta
from pydantic import ValidationError

from app.schemas.auth import SignUpRequest
from app.schemas.user import UserCreate
from app.schemas.recipe import RecipeCreateDto
from app.schemas.rating import RateRecipeRequest


# =========================================================================
# SignUpRequest
# =========================================================================

class TestSignUpRequest:
    """Validation rules for user registration input."""

    def _valid_payload(self, **overrides) -> dict:
        base = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "Secure123",
            "phone": "+1234567890",
            "dateOfBirth": "2000-01-15",
        }
        base.update(overrides)
        return base

    def test_valid_signup(self):
        req = SignUpRequest(**self._valid_payload())
        assert req.firstName == "John"
        assert req.lastName == "Doe"
        assert req.email == "john@example.com"

    def test_empty_first_name_rejected(self):
        with pytest.raises(ValidationError, match="First name cannot be empty"):
            SignUpRequest(**self._valid_payload(firstName="   "))

    def test_empty_last_name_rejected(self):
        with pytest.raises(ValidationError, match="Last name cannot be empty"):
            SignUpRequest(**self._valid_payload(lastName="  "))

    def test_invalid_phone_rejected(self):
        with pytest.raises(ValidationError, match="Phone number must be"):
            SignUpRequest(**self._valid_payload(phone="abc"))

    def test_valid_phone_with_formatting(self):
        """Phone with dashes/spaces should be cleaned and accepted."""
        req = SignUpRequest(**self._valid_payload(phone="+1 (234) 567-8901"))
        assert req.phone == "+12345678901"

    def test_future_dob_rejected(self):
        future = (date.today() + timedelta(days=1)).isoformat()
        with pytest.raises(ValidationError, match="Date of birth must be in the past"):
            SignUpRequest(**self._valid_payload(dateOfBirth=future))

    def test_short_password_rejected(self):
        with pytest.raises(ValidationError, match="Password must be at least 8 characters"):
            SignUpRequest(**self._valid_payload(password="Short1"))


# =========================================================================
# UserCreate (stricter password rules than SignUpRequest)
# =========================================================================

class TestUserCreate:
    """Password strength validation in UserCreate schema."""

    def _valid_payload(self, **overrides) -> dict:
        base = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "password": "Secure123",
            "phone": "+9876543210",
        }
        base.update(overrides)
        return base

    def test_valid_user_create(self):
        user = UserCreate(**self._valid_payload())
        assert user.email == "jane@example.com"

    def test_password_no_uppercase_rejected(self):
        with pytest.raises(ValidationError, match="uppercase"):
            UserCreate(**self._valid_payload(password="nouppercase1"))

    def test_password_no_lowercase_rejected(self):
        with pytest.raises(ValidationError, match="lowercase"):
            UserCreate(**self._valid_payload(password="NOLOWERCASE1"))

    def test_password_no_digit_rejected(self):
        with pytest.raises(ValidationError, match="number"):
            UserCreate(**self._valid_payload(password="NoDigitsHere"))

    def test_password_too_short_rejected(self):
        with pytest.raises(ValidationError, match="8 characters"):
            UserCreate(**self._valid_payload(password="Ab1"))


# =========================================================================
# RecipeCreateDto
# =========================================================================

class TestRecipeCreateDto:
    """Validation for recipe creation input."""

    def test_valid_recipe(self):
        recipe = RecipeCreateDto(name="Pasta Carbonara", calories=500)
        assert recipe.name == "Pasta Carbonara"
        assert recipe.calories == 500

    def test_calories_below_minimum_rejected(self):
        with pytest.raises(ValidationError):
            RecipeCreateDto(name="Too Low", calories=10)

    def test_calories_above_maximum_rejected(self):
        with pytest.raises(ValidationError):
            RecipeCreateDto(name="Too High", calories=9999)

    def test_calories_at_boundaries_accepted(self):
        low = RecipeCreateDto(name="Min", calories=50)
        high = RecipeCreateDto(name="Max", calories=5000)
        assert low.calories == 50
        assert high.calories == 5000

    def test_optional_fields_default_to_none(self):
        recipe = RecipeCreateDto(name="Simple")
        assert recipe.calories is None
        assert recipe.protein is None
        assert recipe.instructions is None
        assert recipe.ingredients == []


# =========================================================================
# RateRecipeRequest
# =========================================================================

class TestRateRecipeRequest:
    """Validation for recipe rating input."""

    def test_valid_rating(self):
        r = RateRecipeRequest(recipeId=1, rating=5, review="Great!")
        assert r.rating == 5

    def test_rating_below_1_rejected(self):
        with pytest.raises(ValidationError):
            RateRecipeRequest(recipeId=1, rating=0)

    def test_rating_above_5_rejected(self):
        with pytest.raises(ValidationError):
            RateRecipeRequest(recipeId=1, rating=6)

    def test_rating_boundaries_accepted(self):
        r1 = RateRecipeRequest(recipeId=1, rating=1)
        r5 = RateRecipeRequest(recipeId=1, rating=5)
        assert r1.rating == 1
        assert r5.rating == 5

    def test_review_is_optional(self):
        r = RateRecipeRequest(recipeId=1, rating=3)
        assert r.review is None
