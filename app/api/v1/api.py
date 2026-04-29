from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, user_preferences, ingredients, recipes, 
    meal_plans, grocery_lists, inventory, reference_data, files, ai
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
