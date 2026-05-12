from sqlalchemy import Column, Integer, SmallInteger, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class RecipeRating(Base):
    __tablename__ = "recipe_ratings"

    rating_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipe.recipe_id"), nullable=False)
    rating = Column(SmallInteger, nullable=False)  # 1–5
    review = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="ratings")
    recipe = relationship("Recipe", backref="ratings")
