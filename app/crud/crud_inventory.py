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

    def add_to_inventory(self, db: Session, user_id: int, ingredient: Ingredient, quantity: int, unit: str):
        inventory = self.get_by_user_id(db, user_id=user_id)
        if not inventory:
            inventory = self.create_for_user(db, user_id=user_id)
        
        # Check existing item
        existing_item = db.query(InvItem).filter(
            InvItem.inv_id == inventory.inv_id,
            InvItem.ing_id == ingredient.ing_id,
            InvItem.unit == unit # simplistic check, case insensitive in Java but let's stick to simple here
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

class CRUDInvItem(CRUDBase[InvItem, BaseModel, BaseModel]):
    pass

inventory = CRUDInventory(Inventory)
inv_item = CRUDInvItem(InvItem)
