from typing import Optional, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.reference import Diet, Allergy, IngredientTag
from pydantic import BaseModel

class CRUDDiet(CRUDBase[Diet, BaseModel, BaseModel]):
    def get_by_name(self, db: Session, name: str) -> Optional[Diet]:
        return db.query(Diet).filter(Diet.diet_name == name).first()

class CRUDAllergy(CRUDBase[Allergy, BaseModel, BaseModel]):
    def get_by_name(self, db: Session, name: str) -> Optional[Allergy]:
        return db.query(Allergy).filter(Allergy.allergy_name == name).first()

class CRUDIngredientTag(CRUDBase[IngredientTag, BaseModel, BaseModel]):
    def get_by_name(self, db: Session, name: str) -> Optional[IngredientTag]:
        return db.query(IngredientTag).filter(IngredientTag.tag_name == name).first()

diet = CRUDDiet(Diet)
allergy = CRUDAllergy(Allergy)
ingredient_tag = CRUDIngredientTag(IngredientTag)
