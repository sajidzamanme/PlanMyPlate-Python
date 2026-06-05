import pytest
from datetime import date
from app import crud
from app.models.inventory import Inventory, InvItem
from app.models.grocery import GroceryList, GroceryListIngredient
from app.models.recipe import Recipe
from app.schemas.user import UserCreate
from app.schemas.meal_plan import MealPlanRequestDto
from app.schemas.grocery import PurchaseRequestDto, PurchaseItemInfo

def _create_test_recipe(db_session, name: str) -> Recipe:
    recipe = Recipe(
        name=name,
        description="Tasty recipe",
        calories=300,
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    return recipe

class TestGroceriesAndInventories:
    def test_registration_creates_inventory(self, db_session):
        user_in = UserCreate(
            first_name="InvUser",
            last_name="Test",
            email="invuser@test.com",
            password="Secure123",
            phone="+9998887776",
        )
        user = crud.user.create(db_session, obj_in=user_in)
        assert user.user_id is not None
        
        # Verify inventory exists
        inv = crud.inventory.get_by_user_id(db_session, user_id=user.user_id)
        assert inv is not None
        assert inv.user_id == user.user_id

    def test_lazy_inventory_retrieval(self, client, db_session, test_user, auth_headers):
        # Delete inventory if it was created by test_user fixture (just in case)
        existing = crud.inventory.get_by_user_id(db_session, user_id=test_user.user_id)
        if existing:
            db_session.delete(existing)
            db_session.commit()

        # Call GET endpoint, should auto-create instead of 404
        resp = client.get(f"/api/inventory/user/{test_user.user_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["userId"] == test_user.user_id
        assert data["invId"] is not None

        # Verify database record actually exists now
        inv = crud.inventory.get_by_user_id(db_session, user_id=test_user.user_id)
        assert inv is not None

    def test_meal_plan_creation_resets_grocery_list(self, client, db_session, test_user, auth_headers):
        # Create an existing active grocery list with some items
        active_list = GroceryList(user_id=test_user.user_id, status="active", date_created=date.today())
        db_session.add(active_list)
        db_session.commit()
        db_session.refresh(active_list)

        # Create a recipe to use in the meal plan
        recipe = _create_test_recipe(db_session, "Biryani")
        from app.models.ingredient import Ingredient
        from app.models.recipe import RecipeIngredient
        ing = Ingredient(name="Rice", price=1.0)
        db_session.add(ing)
        db_session.commit()
        ri = RecipeIngredient(recipe_id=recipe.recipe_id, ing_id=ing.ing_id, quantity=100.0, unit="g")
        db_session.add(ri)
        db_session.commit()

        # Call create meal plan endpoint
        dto_payload = {
            "recipeIds": [recipe.recipe_id],
            "servingsMultipliers": [1],
            "duration": 7,
            "startDate": str(date.today())
        }
        resp = client.post(f"/api/meal-plans/user/{test_user.user_id}/create", json=dto_payload, headers=auth_headers)
        assert resp.status_code == 201

        # Check that the old list is completed
        db_session.refresh(active_list)
        assert active_list.status == "completed"

        # Check that a new active list is created for the meal plan
        new_active = crud.grocery_list.get_by_user_id_and_status(db_session, user_id=test_user.user_id, status="active")
        assert len(new_active) == 1
        assert new_active[0].list_id != active_list.list_id

    def test_purchase_transfers_to_inventory_correctly(self, client, db_session, test_user, auth_headers):
        # Create user inventory
        inventory = crud.inventory.get_by_user_id(db_session, user_id=test_user.user_id)
        if not inventory:
            inventory = crud.inventory.create_for_user(db_session, user_id=test_user.user_id)

        # Create active grocery list with ingredients
        grocery_list = GroceryList(user_id=test_user.user_id, status="active", date_created=date.today())
        db_session.add(grocery_list)
        db_session.commit()

        # Add ingredient to DB
        from app.models.ingredient import Ingredient
        ing = Ingredient(name="Chicken", price=5.0)
        db_session.add(ing)
        db_session.commit()

        # Add item to grocery list
        item = GroceryListIngredient(list_id=grocery_list.list_id, ing_id=ing.ing_id, quantity=1000.0, unit="g")
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)

        # Purchase part of the item (e.g. 400g out of 1000g)
        purchase_payload = {
            "items": [
                {"itemId": item.id, "quantity": 400.0}
            ]
        }
        resp = client.post(f"/api/grocery-lists/{grocery_list.list_id}/purchase", json=purchase_payload, headers=auth_headers)
        assert resp.status_code == 200

        # Verify remaining quantity is 600g
        db_session.refresh(item)
        assert item.quantity == 600.0

        # Verify 400g was added to inventory
        items = crud.inventory.get_items(db_session, inv_id=inventory.inv_id)
        assert len(items) == 1
        assert items[0].ing_id == ing.ing_id
        assert items[0].quantity == 400.0
        assert items[0].unit == "g"

        # Now purchase the remaining 600g with different unit casing ("G") to test unit case-insensitivity
        purchase_payload2 = {
            "items": [
                {"itemId": item.id, "quantity": 600.0}
            ]
        }
        # Force unit to uppercase in inventory comparison check, wait, the grocery item unit remains "g",
        # but in the purchase method we use match_unit lowercase.
        # Let's add another item with uppercase unit to grocery list to check matching.
        # Wait, if we change the item unit to "G" and purchase, it should match case-insensitively.
        item.unit = "G"
        db_session.add(item)
        db_session.commit()

        resp2 = client.post(f"/api/grocery-lists/{grocery_list.list_id}/purchase", json=purchase_payload2, headers=auth_headers)
        assert resp2.status_code == 200

        # The grocery item is fully purchased (600 - 600 = 0), so it should be deleted
        deleted_item = db_session.query(GroceryListIngredient).filter_by(id=item.id).first()
        assert deleted_item is None

        # Verify inventory has accumulated 1000g under case-insensitive match (since "G" matched "g")
        db_session.refresh(inventory)
        items = crud.inventory.get_items(db_session, inv_id=inventory.inv_id)
        assert len(items) == 1
        assert items[0].quantity == 1000.0
