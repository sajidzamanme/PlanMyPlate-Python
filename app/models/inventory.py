from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Inventory(Base):
    __tablename__ = "inventory"
    
    inv_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    last_update = Column(Date)
    
    user = relationship("User")
    items = relationship("InvItem", back_populates="inventory", cascade="all, delete-orphan")

class InvItem(Base):
    __tablename__ = "inv_item"
    
    item_id = Column(Integer, primary_key=True, index=True)
    inv_id = Column(Integer, ForeignKey("inventory.inv_id"), nullable=False)
    ing_id = Column(Integer, ForeignKey("ingredients.ing_id"), nullable=False)
    quantity = Column(Integer)
    unit = Column(String(50))
    date_added = Column(Date)
    expiry_date = Column(Date)
    
    inventory = relationship("Inventory", back_populates="items")
    ingredient = relationship("Ingredient")
