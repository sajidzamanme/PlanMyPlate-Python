from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.reference import Diet, IngredientTag
from pydantic import BaseModel

class CRUDDiet(CRUDBase[Diet, BaseModel, BaseModel]):
    def get_by_name(self, db: Session, name: str) -> Optional[Diet]:
        return db.query(Diet).filter(Diet.diet_name == name).first()

class CRUDIngredientTag(CRUDBase[IngredientTag, BaseModel, BaseModel]):
    def get_by_name(self, db: Session, name: str) -> Optional[IngredientTag]:
        return db.query(IngredientTag).filter(IngredientTag.tag_name == name).first()

diet = CRUDDiet(Diet)
ingredient_tag = CRUDIngredientTag(IngredientTag)
