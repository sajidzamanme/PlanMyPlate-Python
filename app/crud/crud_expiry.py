from typing import List, Optional, Tuple
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.inventory import Inventory, InvItem
from app.models.ingredient import Ingredient


class CRUDExpiry:
    """
    All expiry-related queries operate on the existing inv_item and inventory
    tables — no new table is needed. The ingredient name is resolved/created
    automatically from the free-text productName supplied by the user.
    """

    # ── helpers ───────────────────────────────────────────────────────────────

    def _get_or_create_ingredient(self, db: Session, product_name: str) -> Ingredient:
        """
        Case-insensitive lookup for an ingredient by name.
        Creates a new ingredient row (price=0) if no match is found.
        """
        ingredient = (
            db.query(Ingredient)
            .filter(func.lower(Ingredient.name) == product_name.strip().lower())
            .first()
        )
        if not ingredient:
            ingredient = Ingredient(name=product_name.strip(), price=0)
            db.add(ingredient)
            db.flush()  # get PK without full commit
        return ingredient

    def _get_or_create_inventory(self, db: Session, user_id: int) -> Inventory:
        """Returns the user's inventory, auto-creating one if it doesn't exist yet."""
        inventory = db.query(Inventory).filter(Inventory.user_id == user_id).first()
        if not inventory:
            inventory = Inventory(user_id=user_id, last_update=date.today())
            db.add(inventory)
            db.flush()
        return inventory

    @staticmethod
    def _compute_days(expiry_date: Optional[date]) -> Optional[int]:
        if expiry_date is None:
            return None
        return (expiry_date - date.today()).days

    # ── write operations ──────────────────────────────────────────────────────

    def add_expiry_item(
        self,
        db: Session,
        *,
        user_id: int,
        product_name: str,
        expiry_date: date,
        quantity: float,
        unit: str,
    ) -> InvItem:
        """
        Add a product with an expiry date to the user's inventory.
        - Resolves (or creates) the ingredient by name.
        - Auto-creates inventory if the user doesn't have one.
        - Always inserts a NEW row — even if the same ingredient already exists
          — because the user bought a new batch with a different expiry date.
        """
        inventory = self._get_or_create_inventory(db, user_id)
        ingredient = self._get_or_create_ingredient(db, product_name)

        item = InvItem(
            inv_id=inventory.inv_id,
            ing_id=ingredient.ing_id,
            quantity=quantity,
            unit=unit,
            date_added=date.today(),
            expiry_date=expiry_date,
        )
        db.add(item)

        # keep inventory.last_update fresh
        inventory.last_update = date.today()
        db.add(inventory)

        db.commit()
        db.refresh(item)
        return item

    def update_expiry_item(
        self,
        db: Session,
        *,
        item: InvItem,
        expiry_date: Optional[date] = None,
        quantity: Optional[float] = None,
        unit: Optional[str] = None,
    ) -> InvItem:
        """Partial update — only supplied fields are changed."""
        changed = False

        if expiry_date is not None:
            item.expiry_date = expiry_date
            changed = True
        if quantity is not None:
            item.quantity = quantity
            changed = True
        if unit is not None:
            item.unit = unit
            changed = True

        if changed:
            db.add(item)
            db.commit()
            db.refresh(item)

        return item

    def delete_expiry_item(self, db: Session, *, item: InvItem) -> None:
        db.delete(item)
        db.commit()

    # ── read operations ───────────────────────────────────────────────────────

    def get_item_by_id(self, db: Session, item_id: int) -> Optional[InvItem]:
        return db.query(InvItem).filter(InvItem.item_id == item_id).first()

    def get_all_expiry_items(self, db: Session, *, user_id: int) -> List[InvItem]:
        """
        All inv_item rows (with an expiry_date) belonging to this user,
        ordered by expiry_date ASC so closest-to-expire appears first.
        """
        return (
            db.query(InvItem)
            .join(Inventory, InvItem.inv_id == Inventory.inv_id)
            .filter(
                Inventory.user_id == user_id,
                InvItem.expiry_date.isnot(None),
            )
            .order_by(InvItem.expiry_date.asc())
            .all()
        )

    def get_soon_to_expire(
        self, db: Session, *, user_id: int, days: int
    ) -> Tuple[List[InvItem], int]:
        """
        Returns (items, expired_count).

        items        — all inv_item rows whose expiry_date is between
                       (today - ∞] and (today + days days], ordered ASC.
                       This deliberately includes already-expired items so
                       the mobile app can surface them with an 'EXPIRED' badge.

        expired_count — how many of those items are already past their date.

        Edge cases:
          days=0  → only items expiring exactly today + already expired.
          days<0  → rejected at the endpoint layer (query param validation).
        """
        cutoff = date.today() + timedelta(days=days)

        items: List[InvItem] = (
            db.query(InvItem)
            .join(Inventory, InvItem.inv_id == Inventory.inv_id)
            .filter(
                Inventory.user_id == user_id,
                InvItem.expiry_date.isnot(None),
                InvItem.expiry_date <= cutoff,
            )
            .order_by(InvItem.expiry_date.asc())
            .all()
        )

        today = date.today()
        expired_count = sum(1 for it in items if it.expiry_date < today)
        return items, expired_count


expiry = CRUDExpiry()
