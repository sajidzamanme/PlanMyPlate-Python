from fastapi import APIRouter
<<<<<<< HEAD

from app.api.v1.endpoints import (
    auth,
    users,
    user_preferences,
    recipes,
    ingredients,
    meal_plans,
    grocery_lists,
    inventory,
    files,
    ai,
)

# Reference data endpoint
from app.api.v1.endpoints import user_preferences  # already imported
try:
    from app.api.v1.endpoints import reference_data
    _has_reference_data = True
except ImportError:
    _has_reference_data = False

api_router = APIRouter()

api_router.include_router(auth.router,             prefix="/auth",             tags=["Auth"])
api_router.include_router(users.router,            prefix="/users",            tags=["Users"])
api_router.include_router(user_preferences.router, prefix="/user-preferences", tags=["User Preferences"])
api_router.include_router(recipes.router,          prefix="/recipes",          tags=["Recipes"])
api_router.include_router(ingredients.router,      prefix="/ingredients",      tags=["Ingredients"])
api_router.include_router(meal_plans.router,       prefix="/meal-plans",       tags=["Meal Plans"])
api_router.include_router(grocery_lists.router,    prefix="/grocery-lists",    tags=["Grocery Lists"])
api_router.include_router(inventory.router,        prefix="/inventory",        tags=["Inventory"])
api_router.include_router(files.router,            prefix="/files",            tags=["Files"])
api_router.include_router(ai.router,               prefix="/ai",               tags=["AI"])

if _has_reference_data:
    api_router.include_router(reference_data.router, prefix="/reference-data", tags=["Reference Data"])
=======
from app.api.v1.endpoints import (
    auth, users, user_preferences, ingredients, recipes,
    meal_plans, grocery_lists, inventory, reference_data, files, ai,
    expiry, admin,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(user_preferences.router, prefix="/user-preferences", tags=["user-preferences"])
api_router.include_router(ingredients.router, prefix="/ingredients", tags=["ingredients"])
api_router.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
api_router.include_router(meal_plans.router, prefix="/meal-plans", tags=["meal-plans"])
api_router.include_router(grocery_lists.router, prefix="/grocery-lists", tags=["grocery-lists"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(reference_data.router, prefix="/reference-data", tags=["reference-data"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(expiry.router, prefix="/expiry", tags=["expiry"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
>>>>>>> 8bfbfb597cfd63ddae450134a8d51ecded8fee4b
