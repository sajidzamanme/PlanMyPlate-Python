from sqlalchemy import Column, Integer, String
from app.db.base_class import Base

class Diet(Base):
    __tablename__ = "diets"
    
    diet_id = Column(Integer, primary_key=True, index=True)
    diet_name = Column(String(50), unique=True, nullable=False)

class IngredientTag(Base):
    __tablename__ = "ingredient_tags"
    
    tag_id = Column(Integer, primary_key=True, index=True)
    tag_name = Column(String(50), unique=True, nullable=False)
