from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Recipe(Base):
    __tablename__ = "recipe"
    
    recipe_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    calories = Column(Integer)
    prep_time = Column(Integer)
    cook_time = Column(Integer)
    servings = Column(Integer)
    instructions = Column(Text)
    image_url = Column(String(255))
    
    # Relationship to RecipeIngredient
    recipe_ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipe.recipe_id"), nullable=False)
    ing_id = Column(Integer, ForeignKey("ingredients.ing_id"), nullable=False)
    quantity = Column(Float)
    unit = Column(String(50))
    
    recipe = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient = relationship("Ingredient")
