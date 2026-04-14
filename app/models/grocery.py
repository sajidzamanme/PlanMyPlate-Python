from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class GroceryList(Base):
    __tablename__ = "grocery_list"
    
    list_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    date_created = Column(Date)
    status = Column(String(50))
    
    user = relationship("User")
    items = relationship("GroceryListIngredient", back_populates="grocery_list", cascade="all, delete-orphan")

class GroceryListIngredient(Base):
    __tablename__ = "grocery_list_ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("grocery_list.list_id"), nullable=False)
    ing_id = Column(Integer, ForeignKey("ingredients.ing_id"), nullable=False)
    quantity = Column(Integer, default=1)
    unit = Column(String(50), default="unit")
    
    grocery_list = relationship("GroceryList", back_populates="items")
    ingredient = relationship("Ingredient")
