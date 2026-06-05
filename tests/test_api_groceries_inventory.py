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

    def test_grocery_list_aggregates_duplicates(self, db_session, test_user):
        # Ensure clean state by deleting active grocery lists
        crud.grocery_list.deactivate_active_lists(db_session, user_id=test_user.user_id)

        from app.models.ingredient import Ingredient
        from app.schemas.ingredient import IngredientQuantityDto

        # Setup test ingredients
        ing = Ingredient(name="Garlic", price=2.0)
        db_session.add(ing)
        db_session.commit()

        # Build list containing duplicates with different unit casing ("g" vs "G" vs " g ")
        ing_qty_dto = {
            "ingId": ing.ing_id,
            "name": ing.name,
            "price": float(ing.price)
        }
        
        from app.schemas.ingredient import Ingredient as SchemaIngredient
        schema_ing = SchemaIngredient(**ing_qty_dto)
        
        ingredients_input = [
            IngredientQuantityDto(ingredient=schema_ing, quantity=10.0, unit="g"),
            IngredientQuantityDto(ingredient=schema_ing, quantity=25.0, unit="G"),
            IngredientQuantityDto(ingredient=schema_ing, quantity=5.0, unit=" g ")
        ]

        # Call method
        crud.grocery_list.add_ingredients_with_quantities(
            db_session, user_id=test_user.user_id, ingredient_data=ingredients_input
        )

        # Query database and verify only ONE row exists and is aggregated to 40.0g
        active_lists = crud.grocery_list.get_by_user_id_and_status(db_session, user_id=test_user.user_id, status="active")
        assert len(active_lists) == 1
        items = active_lists[0].items
        assert len(items) == 1
        assert items[0].ing_id == ing.ing_id
        assert items[0].quantity == 40.0
        assert items[0].unit.strip().lower() == "g"

    def test_inventory_add_item_prevents_duplicate(self, db_session, test_user):
        # Get or create inventory
        inventory = crud.inventory.get_by_user_id(db_session, user_id=test_user.user_id)
        if not inventory:
            inventory = crud.inventory.create_for_user(db_session, user_id=test_user.user_id)

        from app.models.ingredient import Ingredient
        ing = Ingredient(name="Milk", price=1.5)
        db_session.add(ing)
        db_session.commit()

        # Add duplicate items with same ingredient, matching unit casing, and same expiry date
        from app.schemas.inventory import InvItemCreateRequest
        
        expiry = date(2026, 7, 7)
        req1 = InvItemCreateRequest(ingId=ing.ing_id, quantity=2.0, unit="Litre", expiryDate=expiry)
        req2 = InvItemCreateRequest(ingId=ing.ing_id, quantity=3.0, unit="litre", expiryDate=expiry)

        crud.inventory.add_item(db_session, inv_id=inventory.inv_id, obj_in=req1)
        crud.inventory.add_item(db_session, inv_id=inventory.inv_id, obj_in=req2)

        # Verify only one inventory item row was created, total quantity = 5.0
        items = crud.inventory.get_items(db_session, inv_id=inventory.inv_id)
        assert len(items) == 1
        assert items[0].quantity == 5.0
        assert items[0].unit == "Litre"
        assert items[0].expiry_date == expiry

    def test_expiry_system_prevents_duplicate(self, db_session, test_user):
        # Clean state
        inventory = crud.inventory.get_by_user_id(db_session, user_id=test_user.user_id)
        if not inventory:
            inventory = crud.inventory.create_for_user(db_session, user_id=test_user.user_id)
            
        # Delete existing items in user inventory to keep it clean
        db_session.query(InvItem).filter(InvItem.inv_id == inventory.inv_id).delete()
        db_session.commit()

        # Call add_expiry_item twice with same parameters
        expiry = date(2026, 8, 8)
        crud.expiry.add_expiry_item(
            db_session,
            user_id=test_user.user_id,
            product_name="Bread",
            expiry_date=expiry,
            quantity=1.0,
            unit="Pack"
        )
        crud.expiry.add_expiry_item(
            db_session,
            user_id=test_user.user_id,
            product_name="Bread",
            expiry_date=expiry,
            quantity=2.0,
            unit="pack"
        )

        # Verify only one row was created, quantity = 3.0
        items = crud.expiry.get_all_expiry_items(db_session, user_id=test_user.user_id)
        assert len(items) == 1
        assert items[0].quantity == 3.0
        assert items[0].unit == "Pack"
        assert items[0].expiry_date == expiry

    def test_cook_recipe_preflight_checks_and_force(self, client, db_session, test_user, auth_headers):
        # 1. Create ingredient and recipe
        from app.models.ingredient import Ingredient
        from app.models.recipe import RecipeIngredient
        from app.models.inventory import InvItem
        
        ing = Ingredient(name="TestIngredientA", price=2.0)
        db_session.add(ing)
        db_session.commit()
        
        recipe = _create_test_recipe(db_session, "TestRecipeA")
        ri = RecipeIngredient(recipe_id=recipe.recipe_id, ing_id=ing.ing_id, quantity=500.0, unit="g")
        db_session.add(ri)
        db_session.commit()
        
        # 2. Get inventory
        inventory = crud.inventory.get_by_user_id(db_session, user_id=test_user.user_id)
        if not inventory:
            inventory = crud.inventory.create_for_user(db_session, user_id=test_user.user_id)
            
        # Clean any existing items in inventory to avoid side-effects
        db_session.query(InvItem).filter(InvItem.inv_id == inventory.inv_id).delete()
        db_session.commit()
        
        # 3. Try cooking without ingredient -> should fail with 409
        resp = client.post(f"/api/recipes/{recipe.recipe_id}/cook", headers=auth_headers)
        assert resp.status_code == 409
        data = resp.json()
        assert data["status"] == "insufficient_ingredients"
        assert data["title"] == "Missing Pantry Items"
        assert data["message"] == "missing inventory item"
        assert len(data["missing"]) == 1
        assert data["missing"][0]["ingId"] == ing.ing_id
        assert data["missing"][0]["required"] == 500.0
        assert data["missing"][0]["available"] == 0.0
        
        # 4. Add insufficient quantity (200g) to inventory
        inv_item = InvItem(
            inv_id=inventory.inv_id,
            ing_id=ing.ing_id,
            quantity=200.0,
            unit="g",
            date_added=date.today()
        )
        db_session.add(inv_item)
        db_session.commit()
        
        # 5. Try cooking -> should fail with 409, available = 200.0
        resp = client.post(f"/api/recipes/{recipe.recipe_id}/cook", headers=auth_headers)
        assert resp.status_code == 409
        data = resp.json()
        assert data["missing"][0]["available"] == 200.0
        
        # 6. Cook with force=true -> should succeed and delete the inventory item (since 200 - 500 <= 0)
        resp = client.post(f"/api/recipes/{recipe.recipe_id}/cook?force=true", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["message"] == "Recipe cooked and ingredients deducted from inventory"
        
        db_session.refresh(inventory)
        items = crud.inventory.get_items(db_session, inv_id=inventory.inv_id)
        assert len(items) == 0

    def test_cook_recipe_fifo_expiry_and_casing(self, client, db_session, test_user, auth_headers):
        from app.models.ingredient import Ingredient
        from app.models.recipe import RecipeIngredient
        from app.models.inventory import InvItem
        
        ing = Ingredient(name="TestIngredientB", price=2.0)
        db_session.add(ing)
        db_session.commit()
        
        recipe = _create_test_recipe(db_session, "TestRecipeB")
        ri = RecipeIngredient(recipe_id=recipe.recipe_id, ing_id=ing.ing_id, quantity=500.0, unit="g")
        db_session.add(ri)
        db_session.commit()
        
        inventory = crud.inventory.get_by_user_id(db_session, user_id=test_user.user_id)
        if not inventory:
            inventory = crud.inventory.create_for_user(db_session, user_id=test_user.user_id)
            
        # Clean inventory
        db_session.query(InvItem).filter(InvItem.inv_id == inventory.inv_id).delete()
        db_session.commit()
        
        # Add Item A (expiring 2026-06-10) - unit "G" (case-insensitive test)
        item_a = InvItem(
            inv_id=inventory.inv_id,
            ing_id=ing.ing_id,
            quantity=300.0,
            unit="G",
            date_added=date.today(),
            expiry_date=date(2026, 6, 10)
        )
        # Add Item B (expiring 2026-06-12) - unit "g"
        item_b = InvItem(
            inv_id=inventory.inv_id,
            ing_id=ing.ing_id,
            quantity=400.0,
            unit="g",
            date_added=date.today(),
            expiry_date=date(2026, 6, 12)
        )
        db_session.add(item_a)
        db_session.add(item_b)
        db_session.commit()
        
        # Cook recipe -> A is deleted, B has 200 remaining
        resp = client.post(f"/api/recipes/{recipe.recipe_id}/cook", headers=auth_headers)
        assert resp.status_code == 200
        
        # Query db directly
        db_session.expire_all()
        items = crud.inventory.get_items(db_session, inv_id=inventory.inv_id)
        assert len(items) == 1
        assert items[0].quantity == 200.0
        assert items[0].expiry_date == date(2026, 6, 12)

    def test_cook_meal_slot(self, client, db_session, test_user, auth_headers):
        from app.models.ingredient import Ingredient
        from app.models.recipe import RecipeIngredient
        from app.models.inventory import InvItem
        from app.models.meal_plan import MealPlan, MealSlot
        
        ing = Ingredient(name="TestIngredientC", price=2.0)
        db_session.add(ing)
        db_session.commit()
        
        recipe = _create_test_recipe(db_session, "TestRecipeC")
        ri = RecipeIngredient(recipe_id=recipe.recipe_id, ing_id=ing.ing_id, quantity=100.0, unit="g")
        db_session.add(ri)
        db_session.commit()
        
        inventory = crud.inventory.get_by_user_id(db_session, user_id=test_user.user_id)
        if not inventory:
            inventory = crud.inventory.create_for_user(db_session, user_id=test_user.user_id)
            
        # Clean inventory
        db_session.query(InvItem).filter(InvItem.inv_id == inventory.inv_id).delete()
        
        # Add 300g to inventory
        inv_item = InvItem(
            inv_id=inventory.inv_id,
            ing_id=ing.ing_id,
            quantity=300.0,
            unit="g",
            date_added=date.today()
        )
        db_session.add(inv_item)
        db_session.commit()
        
        # Create meal plan with servings_multiplier = 2
        # Requires 100 * 2 = 200g
        meal_plan = MealPlan(user_id=test_user.user_id, start_date=date.today(), duration=7, status="active")
        db_session.add(meal_plan)
        db_session.commit()
        db_session.refresh(meal_plan)
        
        slot = MealSlot(
            mp_id=meal_plan.mp_id,
            recipe_id=recipe.recipe_id,
            slot_index=0,
            meal_type="Breakfast",
            day_number=1,
            servings_multiplier=2
        )
        db_session.add(slot)
        db_session.commit()
        db_session.refresh(slot)
        
        # Cook slot
        resp = client.post(f"/api/meal-plans/slots/{slot.id}/cook", headers=auth_headers)
        assert resp.status_code == 200
        
        db_session.expire_all()
        items = crud.inventory.get_items(db_session, inv_id=inventory.inv_id)
        assert len(items) == 1
        assert items[0].quantity == 100.0

    def test_cook_via_inventory_endpoint(self, client, db_session, test_user, auth_headers):
        from app.models.ingredient import Ingredient
        from app.models.recipe import RecipeIngredient
        from app.models.inventory import InvItem
        
        ing = Ingredient(name="TestIngredientD", price=2.0)
        db_session.add(ing)
        db_session.commit()
        
        recipe = _create_test_recipe(db_session, "TestRecipeD")
        ri = RecipeIngredient(recipe_id=recipe.recipe_id, ing_id=ing.ing_id, quantity=100.0, unit="g")
        db_session.add(ri)
        db_session.commit()
        
        inventory = crud.inventory.get_by_user_id(db_session, user_id=test_user.user_id)
        if not inventory:
            inventory = crud.inventory.create_for_user(db_session, user_id=test_user.user_id)
            
        # Clean inventory
        db_session.query(InvItem).filter(InvItem.inv_id == inventory.inv_id).delete()
        
        # Add 300g to inventory
        inv_item = InvItem(
            inv_id=inventory.inv_id,
            ing_id=ing.ing_id,
            quantity=300.0,
            unit="g",
            date_added=date.today()
        )
        db_session.add(inv_item)
        db_session.commit()
        
        # Cook via inventory endpoint
        resp = client.post(f"/api/inventory/cook?recipeId={recipe.recipe_id}&servings=2", headers=auth_headers)
        assert resp.status_code == 200
        
        db_session.expire_all()
        items = crud.inventory.get_items(db_session, inv_id=inventory.inv_id)
        assert len(items) == 1
        assert items[0].quantity == 100.0


