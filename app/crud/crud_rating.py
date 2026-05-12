from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.rating import RecipeRating


class CRUDRating:
    def upsert_rating(
        self,
        db: Session,
        *,
        user_id: int,
        recipe_id: int,
        rating: int,
        review: Optional[str] = None,
    ) -> RecipeRating:
        """Insert or update a user's rating for a recipe."""
        existing = (
            db.query(RecipeRating)
            .filter(
                RecipeRating.user_id == user_id,
                RecipeRating.recipe_id == recipe_id,
            )
            .first()
        )
        if existing:
            existing.rating = rating
            existing.review = review
            db.commit()
            db.refresh(existing)
            return existing

        db_obj = RecipeRating(
            user_id=user_id,
            recipe_id=recipe_id,
            rating=rating,
            review=review,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_user_rating(
        self, db: Session, *, user_id: int, recipe_id: int
    ) -> Optional[RecipeRating]:
        """Get the current user's rating for a specific recipe."""
        return (
            db.query(RecipeRating)
            .filter(
                RecipeRating.user_id == user_id,
                RecipeRating.recipe_id == recipe_id,
            )
            .first()
        )

    def get_recipe_ratings(
        self, db: Session, *, recipe_id: int
    ) -> List[RecipeRating]:
        """List all ratings for a given recipe."""
        return (
            db.query(RecipeRating)
            .filter(RecipeRating.recipe_id == recipe_id)
            .all()
        )

    def get_rating_summary(
        self, db: Session, *, recipe_id: int
    ) -> dict:
        """Return average rating and total count for a recipe."""
        result = (
            db.query(
                func.avg(RecipeRating.rating).label("avg_rating"),
                func.count(RecipeRating.rating_id).label("total"),
            )
            .filter(RecipeRating.recipe_id == recipe_id)
            .first()
        )
        return {
            "recipeId": recipe_id,
            "averageRating": round(float(result.avg_rating or 0), 2),
            "totalRatings": result.total or 0,
        }

    def delete_rating(
        self, db: Session, *, user_id: int, recipe_id: int
    ) -> bool:
        """Delete a user's rating. Returns True if a row was deleted."""
        rows = (
            db.query(RecipeRating)
            .filter(
                RecipeRating.user_id == user_id,
                RecipeRating.recipe_id == recipe_id,
            )
            .delete()
        )
        db.commit()
        return rows > 0


rating = CRUDRating()
