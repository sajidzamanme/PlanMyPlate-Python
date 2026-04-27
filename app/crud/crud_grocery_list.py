from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import date
from pydantic import BaseModel
from app.crud.base import CRUDBase
from app.models.grocery import GroceryList, GroceryListIngredient
from app.schemas.grocery import GroceryListCreate, PurchaseItemInfo
from app.schemas.ingredient import IngredientQuantityDto
from app.models.user import User
from app.models.ingredient import Ingredient
from app.crud.crud_inventory import inventory as crud_inventory

class CRUDGroceryList(CRUDBase[GroceryList, GroceryListCreate, BaseModel]):
    def get_by_user_id(self, db: Session, user_id: int) -> List[GroceryList]:
        return db.query(GroceryList).filter(GroceryList.user_id == user_id).all()

    def get_by_user_id_and_status(self, db: Session, user_id: int, status: str) -> List[GroceryList]:
        return db.query(GroceryList).filter(GroceryList.user_id == user_id, GroceryList.status == status).all()

    def deactivate_active_lists(self, db: Session, user_id: int):
        active_lists = self.get_by_user_id_and_status(db, user_id=user_id, status="active")
        for lst in active_lists:
            lst.status = "completed"
            db.add(lst)
        db.commit()

    def add_ingredients_with_quantities(self, db: Session, user_id: int, ingredient_data: List[IngredientQuantityDto]):
        if not ingredient_data:
            return
        
        # Find active list or create new
        active_lists = self.get_by_user_id_and_status(db, user_id=user_id, status="active")
        if active_lists:
            grocery_list = active_lists[0]
        else:
            grocery_list = GroceryList(
                user_id=user_id,
                date_created=date.today(),
                status="active"
            )
            db.add(grocery_list)
            db.commit()
            db.refresh(grocery_list)
        
        for data in ingredient_data:
            # Check existing
            existing_item = db.query(GroceryListIngredient).filter(
                GroceryListIngredient.list_id == grocery_list.list_id,
                GroceryListIngredient.ing_id == data.ingredient.ingId,
                GroceryListIngredient.unit == data.unit
            ).first()
            
            if existing_item:
                existing_item.quantity += data.quantity
                db.add(existing_item)
            else:
                new_item = GroceryListIngredient(
                    list_id=grocery_list.list_id,
                    ing_id=data.ingredient.ingId,
                    quantity=data.quantity,
                    unit=data.unit
                )
                db.add(new_item)
        
        db.commit()

    def purchase_items(self, db: Session, list_id: int, items: List[PurchaseItemInfo]):
        grocery_list = self.get(db, id=list_id)
        if not grocery_list:
            return
        
        purchase_map = {item.itemId: item.quantity for item in items}
        
        # Use a copy of items to avoid modification issues during iteration if needed
        # But here we are iterating DB objects.
        # Need to be careful.
        
        # db.refresh(grocery_list) # ensure items are loaded
        # Actually grocery_list.items might be lazy loaded.
        
        for item in list(grocery_list.items): # iterate copy
            if item.id in purchase_map:
                purchased_qty = purchase_map[item.id]
                
                # Add to inventory
                crud_inventory.add_to_inventory(
                    db, 
                    user_id=grocery_list.user_id, 
                    ingredient=item.ingredient, 
                    quantity=purchased_qty, 
                    unit=item.unit
                )
                
                # Update grocery list
                remaining_qty = item.quantity - purchased_qty
                if remaining_qty <= 0:
                    db.delete(item)
                else:
                    item.quantity = remaining_qty
                    db.add(item)
        
        db.commit()

class CRUDGroceryListItem(CRUDBase[GroceryListIngredient, BaseModel, BaseModel]):
    pass

grocery_list = CRUDGroceryList(GroceryList)
grocery_list_item = CRUDGroceryListItem(GroceryListIngredient)
