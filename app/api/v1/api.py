from fastapi import APIRouter

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

# Optional endpoints added by origin/main
try:
    from app.api.v1.endpoints import reference_data
    _has_reference_data = True
except ImportError:
    _has_reference_data = False

try:
    from app.api.v1.endpoints import expiry
    _has_expiry = True
except ImportError:
    _has_expiry = False

try:
    from app.api.v1.endpoints import admin
    _has_admin = True
except ImportError:
    _has_admin = False

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

if _has_expiry:
    api_router.include_router(expiry.router, prefix="/expiry", tags=["Expiry"])

if _has_admin:
    api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
