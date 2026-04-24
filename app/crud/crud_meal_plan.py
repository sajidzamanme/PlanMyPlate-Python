from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import date
from app.crud.base import CRUDBase
from app.models.meal_plan import MealPlan, MealSlot
from app.schemas.meal_plan import MealPlanCreate, MealPlanUpdate, MealPlanRequestDto
from app.models.user import User
from app.models.recipe import Recipe
from app.crud.crud_recipe import recipe as crud_recipe
from app.crud.crud_grocery_list import grocery_list as crud_grocery_list

class CRUDMealPlan(CRUDBase[MealPlan, MealPlanCreate, MealPlanUpdate]):
    def get_by_user_id(self, db: Session, user_id: int) -> List[MealPlan]:
        return db.query(MealPlan).filter(MealPlan.user_id == user_id).all()

    def get_by_user_id_and_status(self, db: Session, user_id: int, status: str) -> List[MealPlan]:
        return db.query(MealPlan).filter(MealPlan.user_id == user_id, MealPlan.status == status).all()

    def deactivate_active_plans(self, db: Session, user_id: int):
        active_plans = self.get_by_user_id_and_status(db, user_id=user_id, status="active")
        for plan in active_plans:
            plan.status = "inactive"
            db.add(plan)
        db.commit()

    def create_simple(self, db: Session, *, user_id: int, obj_in: MealPlanCreate) -> MealPlan:
        self.deactivate_active_plans(db, user_id=user_id)
        # Also deactivate grocery lists (logic from Java service)
        crud_grocery_list.deactivate_active_lists(db, user_id=user_id)
        
        db_obj = MealPlan(
            user_id=user_id,
            start_date=obj_in.startDate or date.today(),
            duration=obj_in.duration,
            status=obj_in.status
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_with_recipes(self, db: Session, *, user_id: int, dto: MealPlanRequestDto) -> MealPlan:
        self.deactivate_active_plans(db, user_id=user_id)
        crud_grocery_list.deactivate_active_lists(db, user_id=user_id)
        
        meal_plan = MealPlan(
            user_id=user_id,
            start_date=dto.startDate or date.today(),
            duration=dto.duration,
            status="active"
        )
        db.add(meal_plan)
        db.commit()
        db.refresh(meal_plan)
        
        if dto.recipeIds:
            recipe_ids = dto.recipeIds
            for i, recipe_id in enumerate(recipe_ids):
                if i >= 21: break # limit 21
                
                recipe = crud_recipe.get(db, id=recipe_id)
                if not recipe: continue
                
                day = (i // 3) + 1
                type_index = i % 3
                meal_type = "Breakfast" if type_index == 0 else ("Lunch" if type_index == 1 else "Dinner")
                
                slot = MealSlot(
                    mp_id=meal_plan.mp_id,
                    recipe_id=recipe_id,
                    slot_index=i,
                    day_number=day,
                    meal_type=meal_type
                )
                db.add(slot)
            db.commit()
            db.refresh(meal_plan)
            
            # Logic to populate grocery list would go here or be triggered.
            # Java: calls groceryListService.addIngredientsWithQuantities
            # I will implement this logic in the endpoint using Grocery CRUD/Service.
            
        return meal_plan

    def get_weekly_plans(self, db: Session, user_id: int) -> List[MealPlan]:
        return db.query(MealPlan).filter(
            MealPlan.user_id == user_id, 
            MealPlan.duration == 7,
            MealPlan.status == "active" # Java filters by active in stream
        ).all()

meal_plan = CRUDMealPlan(MealPlan)
