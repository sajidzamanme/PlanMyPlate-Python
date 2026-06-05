import pytest
from datetime import date
from sqlalchemy.orm import Session

from app.models.user import User, UserPreferences
from app.models.recipe import Recipe
from app.models.reference import Diet
from app.crud.crud_user import user as crud_user
from app.crud.crud_recipe import recipe as crud_recipe
from app.crud.crud_favorite import favorite as crud_favorite
from app.crud.crud_user_preferences import user_preferences as crud_user_preferences
from app.schemas.user import UserCreate, UserPreferencesDto
from app.schemas.recipe import RecipeCreateDto
from fastapi.testclient import TestClient


def _create_diet(db: Session, name: str) -> Diet:
    diet = db.query(Diet).filter(Diet.diet_name == name).first()
    if not diet:
        diet = Diet(diet_name=name)
        db.add(diet)
        db.commit()
        db.refresh(diet)
    return diet


class TestUserSoftDelete:
    def test_soft_delete_user_flow(self, db_session: Session):
        # 1. Create a user
        user_in = UserCreate(
            first_name="Soft",
            last_name="Delete",
            email="softdelete@test.com",
            password="SecurePassword123",
            phone="+9999999999",
        )
        user = crud_user.create(db_session, obj_in=user_in)
        user_id = user.user_id
        assert user_id is not None
        assert user.is_deleted is False

        # Verify lookup works
        assert crud_user.get(db_session, id=user_id) is not None
        assert crud_user.get_by_email(db_session, email="softdelete@test.com") is not None
        assert crud_user.get_by_phone(db_session, phone="+9999999999") is not None
        assert crud_user.authenticate(db_session, identifier="softdelete@test.com", password="SecurePassword123") is not None

        # 2. Soft delete user
        crud_user.remove(db_session, id=user_id)

        # 3. Verify they are marked deleted in database
        db_session.expire_all()
        db_record = db_session.query(User).filter(User.user_id == user_id).first()
        assert db_record is not None
        assert db_record.is_deleted is True
        assert db_record.email == f"softdelete@test.com_deleted_{user_id}"
        assert db_record.phone == f"+9999999999_deleted_{user_id}"

        # 4. Verify API lookups return None
        assert crud_user.get(db_session, id=user_id) is None
        assert crud_user.get_by_email(db_session, email="softdelete@test.com") is None
        assert crud_user.get_by_phone(db_session, phone="+9999999999") is None
        assert crud_user.authenticate(db_session, identifier="softdelete@test.com", password="SecurePassword123") is None

        # 5. Verify a new user can register using the original email and phone
        user_new_in = UserCreate(
            first_name="New",
            last_name="User",
            email="softdelete@test.com",
            password="SecurePassword123",
            phone="+9999999999",
        )
        user_new = crud_user.create(db_session, obj_in=user_new_in)
        assert user_new.user_id != user_id
        assert user_new.email == "softdelete@test.com"
        assert user_new.phone == "+9999999999"


class TestRecipeSoftDelete:
    def test_soft_delete_recipe_flow(self, db_session: Session, test_user: User):
        # 1. Create a recipe
        recipe_in = RecipeCreateDto(
            name="Soft Delete Soup",
            description="Testing soft delete",
            calories=150,
            prepTime=10,
            cookTime=15,
            ingredients=[],
        )
        recipe = crud_recipe.create_recipe(db_session, obj_in=recipe_in)
        recipe_id = recipe.recipe_id
        assert recipe_id is not None
        assert recipe.is_deleted is False

        # Verify lookups work
        assert crud_recipe.get(db_session, id=recipe_id) is not None
        assert recipe in crud_recipe.get_multi(db_session)
        assert recipe in crud_recipe.search_by_name(db_session, name="Soup")
        assert recipe in crud_recipe.filter_by_calories(db_session, min_cals=100, max_cals=200)

        # Favorite the recipe
        crud_favorite.add_favorite(db_session, user_id=test_user.user_id, recipe_id=recipe_id)
        assert crud_favorite.is_favorite(db_session, user_id=test_user.user_id, recipe_id=recipe_id) is True
        favorites = crud_favorite.get_user_favorites(db_session, user_id=test_user.user_id)
        assert any(f.recipe_id == recipe_id for f in favorites)

        # 2. Soft delete the recipe
        crud_recipe.remove(db_session, id=recipe_id)

        # 3. Verify recipe is soft-deleted
        db_session.expire_all()
        db_record = db_session.query(Recipe).filter(Recipe.recipe_id == recipe_id).first()
        assert db_record is not None
        assert db_record.is_deleted is True

        # 4. Verify API lookups return None or exclude the recipe
        assert crud_recipe.get(db_session, id=recipe_id) is None
        assert recipe_id not in [r.recipe_id for r in crud_recipe.get_multi(db_session)]
        assert recipe_id not in [r.recipe_id for r in crud_recipe.search_by_name(db_session, name="Soup")]
        assert recipe_id not in [r.recipe_id for r in crud_recipe.filter_by_calories(db_session, min_cals=100, max_cals=200)]

        # 5. Verify it is excluded from favorites lookups
        assert crud_favorite.is_favorite(db_session, user_id=test_user.user_id, recipe_id=recipe_id) is False
        favorites_after = crud_favorite.get_user_favorites(db_session, user_id=test_user.user_id)
        assert not any(f.recipe_id == recipe_id for f in favorites_after)


class TestMultiselectableDiets:
    def test_save_and_retrieve_diets(self, db_session: Session, test_user: User, client: TestClient, auth_headers: dict):
        # Ensure diets are seeded
        _create_diet(db_session, "Keto")
        _create_diet(db_session, "Vegan")
        _create_diet(db_session, "Omnivore")

        # 1. Update preferences with two diets via endpoint
        payload = {
            "userId": test_user.user_id,
            "diets": ["Keto", "Vegan"],
            "allergies": [],
            "dislikes": [],
            "budget": 100.0,
            "height": 175.0,
            "weight": 70.0,
            "gender": "male"
        }
        resp = client.post(f"/api/user-preferences/{test_user.user_id}", json=payload, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert set(data["diets"]) == {"Keto", "Vegan"}

        # 2. Retrieve preferences via endpoint and verify
        resp_get = client.get(f"/api/user-preferences/{test_user.user_id}", headers=auth_headers)
        assert resp_get.status_code == 200
        data_get = resp_get.json()
        assert set(data_get["diets"]) == {"Keto", "Vegan"}

        # 3. Update preferences with a different set of diets
        payload_update = {
            "userId": test_user.user_id,
            "diets": ["Vegan", "Omnivore"],
            "allergies": [],
            "dislikes": [],
        }
        resp_put = client.post(f"/api/user-preferences/{test_user.user_id}", json=payload_update, headers=auth_headers)
        assert resp_put.status_code == 200
        data_put = resp_put.json()
        assert set(data_put["diets"]) == {"Vegan", "Omnivore"}
