from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.favorite import UserFavorite


class CRUDFavorite:
    def add_favorite(
        self, db: Session, *, user_id: int, recipe_id: int
    ) -> UserFavorite:
        """Add a recipe to the user's favorites (idempotent)."""
        existing = (
            db.query(UserFavorite)
            .filter(
                UserFavorite.user_id == user_id,
                UserFavorite.recipe_id == recipe_id,
            )
            .first()
        )
        if existing:
            return existing

        db_obj = UserFavorite(user_id=user_id, recipe_id=recipe_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_favorite(
        self, db: Session, *, user_id: int, recipe_id: int
    ) -> bool:
        """Remove a recipe from favorites. Returns True if a row was deleted."""
        rows = (
            db.query(UserFavorite)
            .filter(
                UserFavorite.user_id == user_id,
                UserFavorite.recipe_id == recipe_id,
            )
            .delete()
        )
        db.commit()
        return rows > 0

    def get_user_favorites(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[UserFavorite]:
        """List user's favorite recipes with full recipe data."""
        return (
            db.query(UserFavorite)
            .options(joinedload(UserFavorite.recipe))
            .filter(UserFavorite.user_id == user_id)
            .order_by(UserFavorite.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def is_favorite(
        self, db: Session, *, user_id: int, recipe_id: int
    ) -> bool:
        """Check whether a recipe is in the user's favorites."""
        return (
            db.query(UserFavorite)
            .filter(
                UserFavorite.user_id == user_id,
                UserFavorite.recipe_id == recipe_id,
            )
            .first()
            is not None
        )


favorite = CRUDFavorite()
