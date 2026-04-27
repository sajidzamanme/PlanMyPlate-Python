from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.crud.base import CRUDBase
from app.models.recipe import Recipe, RecipeIngredient
from app.models.ingredient import Ingredient
from app.schemas.recipe import RecipeCreateDto, RecipeIngredientDto
from app import crud

class CRUDRecipe(CRUDBase[Recipe, RecipeCreateDto, RecipeCreateDto]):
    def create_recipe(self, db: Session, *, obj_in: RecipeCreateDto) -> Recipe:
        # Create Recipe
        db_obj = Recipe(
            name=obj_in.name,
            description=obj_in.description,
            calories=obj_in.calories,
            prep_time=obj_in.prepTime,
            cook_time=obj_in.cookTime,
            servings=obj_in.servings,
            instructions=obj_in.instructions,
            image_url=obj_in.imageUrl
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Create RecipeIngredients
        if obj_in.ingredients:
            for ing_dto in obj_in.ingredients:
                # Find ingredient
                ingredient = crud.ingredient.get(db, id=ing_dto.ingId)
                if not ingredient:
                    continue # or raise error
                
                recipe_ing = RecipeIngredient(
                    recipe_id=db_obj.recipe_id,
                    ing_id=ingredient.ing_id,
                    quantity=ing_dto.quantity,
                    unit=ing_dto.unit
                )
                db.add(recipe_ing)
            db.commit()
            db.refresh(db_obj)
            
        return db_obj

    def update_recipe(self, db: Session, *, db_obj: Recipe, obj_in: RecipeCreateDto) -> Recipe:
        # Update scalar fields
        update_data = obj_in.model_dump(exclude={"ingredients"})
        for field, value in update_data.items():
            # Map camelCase to snake_case if needed, but Pydantic model uses camelCase for JSON
            # But here obj_in fields match snake_case arguments in Recipe constructor mostly?
            # Wait, RecipeCreateDto has camelCase: prepTime, cookTime, imageUrl
            # Recipe model has snake_case: prep_time, cook_time, image_url
            
            # Manual mapping or use aliases in Pydantic. 
            # I used camelCase in Pydantic definition.
            # I need to map it.
            if field == "prepTime":
                setattr(db_obj, "prep_time", value)
            elif field == "cookTime":
                setattr(db_obj, "cook_time", value)
            elif field == "imageUrl":
                setattr(db_obj, "image_url", value)
            else:
                setattr(db_obj, field, value)
        
        # Update ingredients
        # Strategy: Clear existing and add new (simple approach used in Java)
        if obj_in.ingredients is not None:
            # Delete existing
            db.query(RecipeIngredient).filter(RecipeIngredient.recipe_id == db_obj.recipe_id).delete()
            
            # Add new
            for ing_dto in obj_in.ingredients:
                ingredient = crud.ingredient.get(db, id=ing_dto.ingId)
                if not ingredient:
                    continue
                
                recipe_ing = RecipeIngredient(
                    recipe_id=db_obj.recipe_id,
                    ing_id=ingredient.ing_id,
                    quantity=ing_dto.quantity,
                    unit=ing_dto.unit
                )
                db.add(recipe_ing)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def search_by_name(self, db: Session, name: str) -> List[Recipe]:
        return db.query(Recipe).filter(Recipe.name.ilike(f"%{name}%")).all()

    def filter_by_calories(self, db: Session, min_cals: int, max_cals: int) -> List[Recipe]:
        return db.query(Recipe).filter(Recipe.calories >= min_cals, Recipe.calories <= max_cals).all()

recipe = CRUDRecipe(Recipe)
