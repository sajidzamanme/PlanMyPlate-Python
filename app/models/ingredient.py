from sqlalchemy import Column, Integer, String, Numeric, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

# Many-to-Many association table
ingredient_tag_map = Table(
    "ingredient_tag_map",
    Base.metadata,
    Column("ing_id", Integer, ForeignKey("ingredients.ing_id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("ingredient_tags.tag_id"), primary_key=True)
)

class Ingredient(Base):
    __tablename__ = "ingredients"
    
    ing_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False, index=True)
    price = Column(Numeric(10, 2))
    
    tags = relationship("IngredientTag", secondary=ingredient_tag_map, backref="ingredients")
