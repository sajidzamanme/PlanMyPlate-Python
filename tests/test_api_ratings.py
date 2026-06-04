"""
Integration tests for /api/ratings/* endpoints.

Tests cover: rate recipe, get summary, get my rating, delete rating.
"""

import pytest
from app.models.recipe import Recipe


def _create_test_recipe(db_session) -> int:
    """Insert a recipe directly into the DB and return its ID."""
    recipe = Recipe(
        name="Ratable Recipe",
        description="A recipe to rate",
        calories=300,
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    return recipe.recipe_id


class TestRateRecipe:
    """POST /api/ratings/"""

    def test_rate_recipe_success(self, client, db_session, test_user, auth_headers):
        recipe_id = _create_test_recipe(db_session)

        resp = client.post(
            "/api/ratings/",
            json={"recipeId": recipe_id, "rating": 4, "review": "Very good!"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["rating"] == 4
        assert data["review"] == "Very good!"
        assert data["recipeId"] == recipe_id

    def test_rate_nonexistent_recipe(self, client, auth_headers):
        resp = client.post(
            "/api/ratings/",
            json={"recipeId": 99999, "rating": 3},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_update_rating_via_upsert(self, client, db_session, test_user, auth_headers):
        """Rating the same recipe again should update, not duplicate."""
        recipe_id = _create_test_recipe(db_session)

        # First rating
        client.post(
            "/api/ratings/",
            json={"recipeId": recipe_id, "rating": 3},
            headers=auth_headers,
        )
        # Update to 5
        resp = client.post(
            "/api/ratings/",
            json={"recipeId": recipe_id, "rating": 5, "review": "Changed my mind!"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["rating"] == 5


class TestGetRatingSummary:
    """GET /api/ratings/recipe/{recipe_id}"""

    def test_rating_summary(self, client, db_session, test_user, auth_headers):
        recipe_id = _create_test_recipe(db_session)

        # Submit a rating
        client.post(
            "/api/ratings/",
            json={"recipeId": recipe_id, "rating": 4},
            headers=auth_headers,
        )

        resp = client.get(f"/api/ratings/recipe/{recipe_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["recipeId"] == recipe_id
        assert data["averageRating"] == 4.0
        assert data["totalRatings"] == 1


class TestDeleteRating:
    """DELETE /api/ratings/{recipe_id}"""

    def test_delete_rating_success(self, client, db_session, test_user, auth_headers):
        recipe_id = _create_test_recipe(db_session)

        # Create then delete
        client.post(
            "/api/ratings/",
            json={"recipeId": recipe_id, "rating": 3},
            headers=auth_headers,
        )

        resp = client.delete(f"/api/ratings/{recipe_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert "deleted" in resp.json()["message"].lower()

    def test_delete_nonexistent_rating(self, client, auth_headers):
        resp = client.delete("/api/ratings/99999", headers=auth_headers)
        assert resp.status_code == 404
