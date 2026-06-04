"""
Integration tests for /api/favorites/* endpoints.

Tests cover: add favorite, check status, list, remove.
"""

import pytest
from app.models.recipe import Recipe


def _create_test_recipe(db_session) -> int:
    """Insert a recipe directly into the DB and return its ID."""
    recipe = Recipe(
        name="Favable Recipe",
        description="A recipe to favorite",
        calories=250,
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    return recipe.recipe_id


class TestAddFavorite:
    """POST /api/favorites/{recipe_id}"""

    def test_add_favorite_success(self, client, db_session, test_user, auth_headers):
        recipe_id = _create_test_recipe(db_session)

        resp = client.post(f"/api/favorites/{recipe_id}", headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["recipeId"] == recipe_id
        assert data["userId"] == test_user.user_id

    def test_add_favorite_nonexistent_recipe(self, client, auth_headers):
        resp = client.post("/api/favorites/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_add_favorite_idempotent(self, client, db_session, test_user, auth_headers):
        """Adding the same favorite twice should not fail."""
        recipe_id = _create_test_recipe(db_session)

        client.post(f"/api/favorites/{recipe_id}", headers=auth_headers)
        resp = client.post(f"/api/favorites/{recipe_id}", headers=auth_headers)
        assert resp.status_code == 201  # idempotent — returns existing


class TestCheckFavoriteStatus:
    """GET /api/favorites/{recipe_id}/status"""

    def test_status_true_after_add(self, client, db_session, test_user, auth_headers):
        recipe_id = _create_test_recipe(db_session)
        client.post(f"/api/favorites/{recipe_id}", headers=auth_headers)

        resp = client.get(f"/api/favorites/{recipe_id}/status", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["isFavorite"] is True

    def test_status_false_when_not_favorited(self, client, db_session, auth_headers):
        recipe_id = _create_test_recipe(db_session)

        resp = client.get(f"/api/favorites/{recipe_id}/status", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["isFavorite"] is False


class TestListFavorites:
    """GET /api/favorites/"""

    def test_list_empty(self, client, auth_headers):
        resp = client.get("/api/favorites/", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_after_adding(self, client, db_session, test_user, auth_headers):
        r1 = _create_test_recipe(db_session)
        r2 = _create_test_recipe(db_session)
        client.post(f"/api/favorites/{r1}", headers=auth_headers)
        client.post(f"/api/favorites/{r2}", headers=auth_headers)

        resp = client.get("/api/favorites/", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestRemoveFavorite:
    """DELETE /api/favorites/{recipe_id}"""

    def test_remove_favorite_success(self, client, db_session, test_user, auth_headers):
        recipe_id = _create_test_recipe(db_session)
        client.post(f"/api/favorites/{recipe_id}", headers=auth_headers)

        resp = client.delete(f"/api/favorites/{recipe_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert "removed" in resp.json()["message"].lower()

        # Verify status is now false
        status = client.get(f"/api/favorites/{recipe_id}/status", headers=auth_headers)
        assert status.json()["isFavorite"] is False

    def test_remove_nonexistent_favorite(self, client, db_session, auth_headers):
        recipe_id = _create_test_recipe(db_session)
        resp = client.delete(f"/api/favorites/{recipe_id}", headers=auth_headers)
        assert resp.status_code == 404
