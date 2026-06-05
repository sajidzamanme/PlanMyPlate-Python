import pytest
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe, RecipeIngredient
from app.models.inventory import Inventory, InvItem
from app.models.grocery import GroceryList, GroceryListIngredient
from app.models.favorite import UserFavorite

@pytest.fixture
def populated_data(db_session, test_user):
    # Create ingredients out of order
    apple = Ingredient(name="Apple", price=1.0)
    banana = Ingredient(name="Banana", price=1.5)
    cherry = Ingredient(name="Cherry", price=2.0)
    db_session.add_all([cherry, banana, apple])
    db_session.commit()
    
    # Create recipes out of order
    salad = Recipe(name="Salad", calories=150)
    burger = Recipe(name="Burger", calories=600)
    pasta = Recipe(name="Pasta", calories=400)
    db_session.add_all([pasta, burger, salad])
    db_session.commit()
    
    # Create recipe ingredients
    ri1 = RecipeIngredient(recipe_id=burger.recipe_id, ing_id=banana.ing_id, quantity=1.0, unit="pcs")
    ri2 = RecipeIngredient(recipe_id=pasta.recipe_id, ing_id=apple.ing_id, quantity=2.0, unit="pcs")
    db_session.add_all([ri1, ri2])
    db_session.commit()
    
    # Create user inventory
    inv = Inventory(user_id=test_user.user_id)
    db_session.add(inv)
    db_session.commit()
    
    # Add inventory items out of order
    inv_cherry = InvItem(inv_id=inv.inv_id, ing_id=cherry.ing_id, quantity=10.0, unit="g")
    inv_apple = InvItem(inv_id=inv.inv_id, ing_id=apple.ing_id, quantity=5.0, unit="g")
    inv_banana = InvItem(inv_id=inv.inv_id, ing_id=banana.ing_id, quantity=2.0, unit="g")
    db_session.add_all([inv_cherry, inv_apple, inv_banana])
    db_session.commit()
    
    # Create grocery list and add items out of order
    glist = GroceryList(user_id=test_user.user_id, status="active")
    db_session.add(glist)
    db_session.commit()
    
    gl_cherry = GroceryListIngredient(list_id=glist.list_id, ing_id=cherry.ing_id, quantity=10.0, unit="g")
    gl_apple = GroceryListIngredient(list_id=glist.list_id, ing_id=apple.ing_id, quantity=5.0, unit="g")
    gl_banana = GroceryListIngredient(list_id=glist.list_id, ing_id=banana.ing_id, quantity=2.0, unit="g")
    db_session.add_all([gl_cherry, gl_apple, gl_banana])
    db_session.commit()
    
    # Add favorites out of order (Burger, Pasta, Salad)
    # Salad added first, Pasta second, Burger third
    fav1 = UserFavorite(user_id=test_user.user_id, recipe_id=salad.recipe_id)
    fav2 = UserFavorite(user_id=test_user.user_id, recipe_id=pasta.recipe_id)
    fav3 = UserFavorite(user_id=test_user.user_id, recipe_id=burger.recipe_id)
    db_session.add_all([fav1, fav2, fav3])
    db_session.commit()
    
    return {
        "ingredients": [apple, banana, cherry],
        "recipes": [burger, pasta, salad],
        "inventory": inv,
        "grocery_list": glist
    }

def test_ingredients_sorted_by_name(client, populated_data):
    resp = client.get("/api/ingredients/")
    assert resp.status_code == 200
    data = resp.json()
    names = [item["name"] for item in data]
    assert names == ["Apple", "Banana", "Cherry"]

def test_ingredients_search_sorted_by_name(client, populated_data):
    resp = client.get("/api/ingredients/search?name=a")
    assert resp.status_code == 200
    data = resp.json()
    names = [item["name"] for item in data]
    # "Apple" and "Banana" contain "a" or "A" (case-insensitive)
    assert names == ["Apple", "Banana"]

def test_recipes_sorted_by_name(client, populated_data):
    resp = client.get("/api/recipes/")
    assert resp.status_code == 200
    data = resp.json()
    names = [item["name"] for item in data]
    assert names == ["Burger", "Pasta", "Salad"]

def test_recipes_search_sorted_by_name(client, populated_data):
    resp = client.get("/api/recipes/search?name=a")
    assert resp.status_code == 200
    data = resp.json()
    names = [item["name"] for item in data]
    # "Pasta" and "Salad" contain "a" or "A" (case-insensitive)
    assert names == ["Pasta", "Salad"]

def test_recipes_filter_calories_sorted_by_name(client, populated_data):
    resp = client.get("/api/recipes/filter/calories?minCalories=100&maxCalories=500")
    assert resp.status_code == 200
    data = resp.json()
    names = [item["name"] for item in data]
    # Salad (150) and Pasta (400) are in this range
    assert names == ["Pasta", "Salad"]

def test_favorites_sorted_by_name(client, auth_headers, populated_data):
    resp = client.get("/api/favorites/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    names = [item["recipe"]["name"] for item in data]
    assert names == ["Burger", "Pasta", "Salad"]

def test_inventory_sorted_by_name(client, auth_headers, populated_data, test_user):
    resp = client.get(f"/api/inventory/user/{test_user.user_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    names = [item["ingredient"]["name"] for item in data["items"]]
    assert names == ["Apple", "Banana", "Cherry"]

def test_inventory_items_endpoint_sorted_by_name(client, auth_headers, populated_data):
    inv_id = populated_data["inventory"].inv_id
    resp = client.get(f"/api/inventory/{inv_id}/items", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    names = [item["ingredient"]["name"] for item in data]
    assert names == ["Apple", "Banana", "Cherry"]

def test_grocery_list_items_sorted_by_name(client, auth_headers, populated_data, test_user):
    resp = client.get(f"/api/grocery-lists/user/{test_user.user_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    names = [item["ingredient"]["name"] for item in data[0]["items"]]
    assert names == ["Apple", "Banana", "Cherry"]
