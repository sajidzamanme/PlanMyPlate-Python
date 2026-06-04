"""
Integration tests for /api/recipes/* endpoints.

Tests cover: CRUD operations, search, and calorie filtering.
"""

import pytest


def _recipe_payload(**overrides) -> dict:
    base = {
        "name": "Test Recipe",
        "description": "Delicious test recipe",
        "calories": 400,
        "protein": 25.0,
        "carbs": 45.0,
        "fat": 12.0,
        "fiber": 6.0,
        "prepTime": 10,
        "cookTime": 20,
        "instructions": "Step 1: Cook. Step 2: Eat.",
        "ingredients": [],
    }
    base.update(overrides)
    return base


class TestListRecipes:
    """GET /api/recipes/"""

    def test_list_empty(self, client):
        resp = client.get("/api/recipes/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_after_creation(self, client):
        client.post("/api/recipes/", json=_recipe_payload(name="Recipe A"))
        client.post("/api/recipes/", json=_recipe_payload(name="Recipe B"))
        resp = client.get("/api/recipes/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestCreateRecipe:
    """POST /api/recipes/"""

    def test_create_success(self, client):
        resp = client.post("/api/recipes/", json=_recipe_payload())
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test Recipe"
        assert data["recipeId"] is not None
        assert data["calories"] == 400


class TestGetRecipe:
    """GET /api/recipes/{id}"""

    def test_get_existing(self, client):
        create_resp = client.post("/api/recipes/", json=_recipe_payload())
        recipe_id = create_resp.json()["recipeId"]

        resp = client.get(f"/api/recipes/{recipe_id}")
        assert resp.status_code == 200
        assert resp.json()["recipeId"] == recipe_id

    def test_get_nonexistent(self, client):
        resp = client.get("/api/recipes/99999")
        assert resp.status_code == 404


class TestUpdateRecipe:
    """PUT /api/recipes/{id}"""

    def test_update_success(self, client):
        create_resp = client.post("/api/recipes/", json=_recipe_payload())
        recipe_id = create_resp.json()["recipeId"]

        updated = _recipe_payload(name="Updated Recipe", calories=500)
        resp = client.put(f"/api/recipes/{recipe_id}", json=updated)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Recipe"
        assert resp.json()["calories"] == 500

    def test_update_nonexistent(self, client):
        resp = client.put("/api/recipes/99999", json=_recipe_payload())
        assert resp.status_code == 404


class TestDeleteRecipe:
    """DELETE /api/recipes/{id}"""

    def test_delete_success(self, client):
        create_resp = client.post("/api/recipes/", json=_recipe_payload())
        recipe_id = create_resp.json()["recipeId"]

        resp = client.delete(f"/api/recipes/{recipe_id}")
        assert resp.status_code == 200
        assert "deleted" in resp.json()["message"].lower()

        # Verify it's gone
        get_resp = client.get(f"/api/recipes/{recipe_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent(self, client):
        resp = client.delete("/api/recipes/99999")
        assert resp.status_code == 404


class TestSearchRecipes:
    """GET /api/recipes/search"""

    def test_search_by_name(self, client):
        client.post("/api/recipes/", json=_recipe_payload(name="Chicken Curry"))
        client.post("/api/recipes/", json=_recipe_payload(name="Chicken Salad"))
        client.post("/api/recipes/", json=_recipe_payload(name="Pasta"))

        resp = client.get("/api/recipes/search", params={"name": "Chicken"})
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 2

    def test_search_no_results(self, client):
        resp = client.get("/api/recipes/search", params={"name": "Sushi"})
        assert resp.status_code == 200
        assert resp.json() == []


class TestFilterByCalories:
    """GET /api/recipes/filter/calories"""

    def test_filter_in_range(self, client):
        client.post("/api/recipes/", json=_recipe_payload(name="Low Cal", calories=200))
        client.post("/api/recipes/", json=_recipe_payload(name="Mid Cal", calories=400))
        client.post("/api/recipes/", json=_recipe_payload(name="High Cal", calories=800))

        resp = client.get(
            "/api/recipes/filter/calories",
            params={"minCalories": 150, "maxCalories": 500},
        )
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 2
        names = {r["name"] for r in results}
        assert "Low Cal" in names
        assert "Mid Cal" in names
