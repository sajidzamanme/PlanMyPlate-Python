from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.crud.base import CRUDBase
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate, IngredientUpdate

class CRUDIngredient(CRUDBase[Ingredient, IngredientCreate, IngredientUpdate]):
    def get_by_name(self, db: Session, name: str) -> Optional[Ingredient]:
        return db.query(Ingredient).filter(Ingredient.name == name).first()

    def search_by_name(self, db: Session, name: str) -> List[Ingredient]:
        return db.query(Ingredient).filter(Ingredient.name.ilike(f"%{name}%")).all()
    
    def filter_by_price(self, db: Session, min_price: float, max_price: float) -> List[Ingredient]:
        return db.query(Ingredient).filter(Ingredient.price >= min_price, Ingredient.price <= max_price).all()

ingredient = CRUDIngredient(Ingredient)
