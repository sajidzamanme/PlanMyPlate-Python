from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class MealPlan(Base):
    __tablename__ = "meal_plan"
    
    mp_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    start_date = Column(Date)
    duration = Column(Integer)
    status = Column(String(50))
    
    user = relationship("User")
    slots = relationship("MealSlot", back_populates="meal_plan", cascade="all, delete-orphan")

class MealSlot(Base):
    __tablename__ = "meal_slot"
    
    id = Column(Integer, primary_key=True, index=True)
    mp_id = Column(Integer, ForeignKey("meal_plan.mp_id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipe.recipe_id"), nullable=False)
    slot_index = Column(Integer, nullable=False)
    meal_type = Column(String(20), nullable=False)
    day_number = Column(Integer, nullable=False)
    
    meal_plan = relationship("MealPlan", back_populates="slots")
    recipe = relationship("Recipe")
