from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user import UserPreferences, User
from app.schemas.user import UserPreferencesDto
from app.models.reference import Diet
from app.models.ingredient import Ingredient
from app.crud.crud_reference import diet as crud_diet
from app.crud.crud_ingredient import ingredient as crud_ingredient

class CRUDUserPreferences(CRUDBase[UserPreferences, UserPreferencesDto, UserPreferencesDto]):
    def get_by_user_id(self, db: Session, user_id: int) -> Optional[UserPreferences]:
        return db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()

    def create_or_update(
        self, db: Session, *, user_id: int, obj_in: UserPreferencesDto
    ) -> UserPreferences:
        db_obj = self.get_by_user_id(db, user_id=user_id)
        if not db_obj:
            db_obj = UserPreferences(user_id=user_id)
            db.add(db_obj)

        if obj_in.diets is not None:
            diets = []
            for name in obj_in.diets:
                diet = crud_diet.get_by_name(db, name=name.strip())
                if diet:
                    diets.append(diet)
            db_obj.diets = diets
        
        if obj_in.allergies:
            allergies = []
            for name in obj_in.allergies:
                ing = crud_ingredient.get_by_name(db, name=name.strip())
                if ing:
                    allergies.append(ing)
            db_obj.allergies = allergies
            
        if obj_in.dislikes:
            dislikes = []
            for name in obj_in.dislikes:
                ing = crud_ingredient.get_by_name(db, name=name.strip())
                if ing:
                    dislikes.append(ing)
            db_obj.dislikes = dislikes
            
        if obj_in.budget is not None:
            db_obj.budget = obj_in.budget

        if obj_in.height is not None:
            db_obj.height = obj_in.height

        if obj_in.weight is not None:
            db_obj.weight = obj_in.weight

        if obj_in.gender is not None:
            db_obj.gender = obj_in.gender
            
        db.commit()
        db.refresh(db_obj)
        return db_obj

user_preferences = CRUDUserPreferences(UserPreferences)
