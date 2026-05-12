from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class UserFavorite(Base):
    __tablename__ = "user_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipe.recipe_id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", backref="favorites")
    recipe = relationship("Recipe", backref="favorited_by")
