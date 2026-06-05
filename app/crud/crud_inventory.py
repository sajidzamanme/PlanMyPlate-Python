from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import date
from pydantic import BaseModel
from app.crud.base import CRUDBase
from app.models.inventory import Inventory, InvItem
from app.schemas.inventory import InvItemCreateRequest
from app.models.user import User
from app.models.ingredient import Ingredient

class CRUDInventory(CRUDBase[Inventory, BaseModel, BaseModel]):
    def get_by_user_id(self, db: Session, user_id: int) -> Optional[Inventory]:
        return db.query(Inventory).filter(Inventory.user_id == user_id).first()

    def create_for_user(self, db: Session, user_id: int) -> Inventory:
        db_obj = Inventory(user_id=user_id, last_update=date.today())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def add_item(self, db: Session, inv_id: int, obj_in: InvItemCreateRequest) -> InvItem:
        # Check if an item with the same ingredient, unit (case-insensitive), and expiry date already exists
        from sqlalchemy import func
        existing_item = db.query(InvItem).filter(
            InvItem.inv_id == inv_id,
            InvItem.ing_id == obj_in.ingId,
            func.lower(InvItem.unit) == (obj_in.unit or "unit").strip().lower(),
            InvItem.expiry_date == obj_in.expiryDate
        ).first()
        
        if existing_item:
            existing_item.quantity += obj_in.quantity
            db_obj = existing_item
        else:
            db_obj = InvItem(
                inv_id=inv_id,
                ing_id=obj_in.ingId,
                quantity=obj_in.quantity,
                unit=obj_in.unit,
                date_added=date.today(),
                expiry_date=obj_in.expiryDate
            )
            db.add(db_obj)
            
        # Update last_update
        inventory = self.get(db, id=inv_id)
        if inventory:
            inventory.last_update = date.today()
            db.add(inventory)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_items(self, db: Session, inv_id: int) -> List[InvItem]:
        return db.query(InvItem).filter(InvItem.inv_id == inv_id).all()

    def add_to_inventory(self, db: Session, user_id: int, ingredient: Ingredient, quantity: float, unit: str):
        inventory = self.get_by_user_id(db, user_id=user_id)
        if not inventory:
            inventory = self.create_for_user(db, user_id=user_id)
        
        # Check existing item case-insensitively
        from sqlalchemy import func
        existing_item = db.query(InvItem).filter(
            InvItem.inv_id == inventory.inv_id,
            InvItem.ing_id == ingredient.ing_id,
            func.lower(InvItem.unit) == unit.strip().lower()
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
            db.add(existing_item)
        else:
            new_item = InvItem(
                inv_id=inventory.inv_id,
                ing_id=ingredient.ing_id,
                quantity=quantity,
                unit=unit,
                date_added=date.today(),
                # Default expiry +7 days? Java logic: "Default expiry date logic could go here"
                # I'll leave expiry null or set default.
            )
            db.add(new_item)
        
        inventory.last_update = date.today()
        db.add(inventory)
        db.commit()

    def check_recipe_ingredients(self, db: Session, user_id: int, recipe_id: int, servings: float = 1.0) -> List[dict]:
        inventory = self.get_by_user_id(db, user_id=user_id)
        if not inventory:
            inventory = self.create_for_user(db, user_id=user_id)
            
        from app.models.recipe import Recipe
        recipe = db.query(Recipe).filter(Recipe.recipe_id == recipe_id).first()
        if not recipe:
            return []
            
        missing_ingredients = []
        from sqlalchemy import func
        for ri in recipe.recipe_ingredients:
            qty_needed = (ri.quantity or 0.0) * servings
            if qty_needed <= 0:
                continue
                
            unit_lower = (ri.unit or "unit").strip().lower()
            
            # Query all inventory items of the same ingredient and unit (case-insensitive)
            items = db.query(InvItem).filter(
                InvItem.inv_id == inventory.inv_id,
                InvItem.ing_id == ri.ing_id,
                func.lower(InvItem.unit) == unit_lower
            ).all()
            
            qty_available = sum(item.quantity or 0.0 for item in items)
            if qty_available < qty_needed:
                missing_ingredients.append({
                    "ingId": ri.ing_id,
                    "name": ri.ingredient.name,
                    "required": qty_needed,
                    "available": qty_available,
                    "unit": ri.unit or "unit"
                })
                
        return missing_ingredients

    def deduct_recipe_ingredients(self, db: Session, user_id: int, recipe_id: int, servings: float = 1.0) -> bool:
        inventory = self.get_by_user_id(db, user_id=user_id)
        if not inventory:
            inventory = self.create_for_user(db, user_id=user_id)
            
        from app.models.recipe import Recipe
        recipe = db.query(Recipe).filter(Recipe.recipe_id == recipe_id).first()
        if not recipe:
            return False
            
        from sqlalchemy import func
        for ri in recipe.recipe_ingredients:
            qty_needed = (ri.quantity or 0.0) * servings
            if qty_needed <= 0:
                continue
                
            unit_lower = (ri.unit or "unit").strip().lower()
            
            # Query all inventory items of the same ingredient and unit (case-insensitive)
            items = db.query(InvItem).filter(
                InvItem.inv_id == inventory.inv_id,
                InvItem.ing_id == ri.ing_id,
                func.lower(InvItem.unit) == unit_lower
            ).all()
            
            # Sort items by expiry date (earliest expiry first, None last)
            items.sort(key=lambda x: (x.expiry_date is None, x.expiry_date))
            
            remaining_to_deduct = qty_needed
            for item in items:
                if remaining_to_deduct <= 0:
                    break
                    
                if (item.quantity or 0.0) <= remaining_to_deduct:
                    remaining_to_deduct -= (item.quantity or 0.0)
                    db.delete(item)
                else:
                    item.quantity -= remaining_to_deduct
                    remaining_to_deduct = 0.0
                    db.add(item)
                    
        inventory.last_update = date.today()
        db.add(inventory)
        db.commit()
        return True


class CRUDInvItem(CRUDBase[InvItem, BaseModel, BaseModel]):
    pass

inventory = CRUDInventory(Inventory)
inv_item = CRUDInvItem(InvItem)
