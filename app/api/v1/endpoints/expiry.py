from typing import Any, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.expiry import (
    ExpiryEntryRequest,
    ExpiryItemUpdateRequest,
    ExpiryItemResponse,
    SoonToExpireResponse,
)

router = APIRouter()


# ── helpers ────────────────────────────────────────────────────────────────────

def _build_response(item) -> ExpiryItemResponse:
    """
    Map an InvItem ORM object → ExpiryItemResponse.
    Computes daysUntilExpiry and isExpired from expiry_date at serialisation time.
    """
    days_until = (
        (item.expiry_date - date.today()).days if item.expiry_date else None
    )
    return ExpiryItemResponse(
        item_id=item.item_id,
        product_name=item.ingredient.name if item.ingredient else "Unknown",
        expiry_date=item.expiry_date,
        date_added=item.date_added,
        quantity=item.quantity,
        unit=item.unit,
        daysUntilExpiry=days_until,
        isExpired=(days_until < 0) if days_until is not None else False,
    )


def _assert_owns_item(item, current_user: User, db: Session):
    """Raise 400 if the item doesn't belong to the authenticated user."""
    from app.models.inventory import Inventory
    inventory = db.query(Inventory).filter_by(inv_id=item.inv_id).first()
    if not inventory or inventory.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")


# ── POST /expiry/user/{user_id}/items ──────────────────────────────────────────

@router.post(
    "/user/{user_id}/items",
    response_model=ExpiryItemResponse,
    status_code=201,
    summary="Add a product with an expiry date",
    description=(
        "Records a purchased product and its expiry date in the user's inventory. "
        "The product name is matched case-insensitively against existing ingredients; "
        "a new ingredient entry is created automatically if no match is found. "
        "An inventory is also auto-created if the user doesn't have one yet."
    ),
)
def add_expiry_item(
    *,
    user_id: int,
    item_in: ExpiryEntryRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    if user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    item = crud.expiry.add_expiry_item(
        db,
        user_id=user_id,
        product_name=item_in.productName,
        expiry_date=item_in.expiryDate,
        quantity=item_in.quantity,
        unit=item_in.unit,
    )
    return _build_response(item)


# ── GET /expiry/user/{user_id}/items ───────────────────────────────────────────

@router.get(
    "/user/{user_id}/items",
    response_model=List[ExpiryItemResponse],
    summary="List all expiry-tracked items for a user",
    description="Returns every inventory item that has an expiry date, ordered soonest-first.",
)
def get_all_expiry_items(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    if user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    items = crud.expiry.get_all_expiry_items(db, user_id=user_id)
    return [_build_response(it) for it in items]


# ── GET /expiry/user/{user_id}/soon ────────────────────────────────────────────

@router.get(
    "/user/{user_id}/soon",
    response_model=SoonToExpireResponse,
    summary="Get soon-to-expire items",
    description=(
        "Returns inventory items expiring within the next `days` days (default 10). "
        "Already-expired items are **included** and flagged with `isExpired=true`. "
        "The mobile app passes the user's configured threshold from Settings; "
        "this endpoint is designed to be called on a schedule from the device."
    ),
)
def get_soon_to_expire(
    user_id: int,
    days: int = Query(
        default=10,
        ge=0,
        le=3650,
        description="Threshold in days (0 = today only, max 3650 ≈ 10 years). "
                    "Pass the value from the user's app settings.",
    ),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    if user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    items, expired_count = crud.expiry.get_soon_to_expire(db, user_id=user_id, days=days)

    return SoonToExpireResponse(
        thresholdDays=days,
        totalCount=len(items),
        expiredCount=expired_count,
        items=[_build_response(it) for it in items],
    )


# ── PUT /expiry/items/{item_id} ────────────────────────────────────────────────

@router.put(
    "/items/{item_id}",
    response_model=ExpiryItemResponse,
    summary="Update an expiry item",
    description="Partially update the expiry date, quantity, or unit of an inventory item. Only supplied fields are changed.",
)
def update_expiry_item(
    *,
    item_id: int,
    item_in: ExpiryItemUpdateRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    item = crud.expiry.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    _assert_owns_item(item, current_user, db)

    # Reject update if new expiry_date leaves item with no date and wasn't set before
    updated = crud.expiry.update_expiry_item(
        db,
        item=item,
        expiry_date=item_in.expiryDate,
        quantity=item_in.quantity,
        unit=item_in.unit,
    )
    return _build_response(updated)


# ── DELETE /expiry/items/{item_id} ─────────────────────────────────────────────

@router.delete(
    "/items/{item_id}",
    summary="Remove an expiry item",
    description="Permanently deletes an inventory item entry.",
)
def delete_expiry_item(
    *,
    item_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    item = crud.expiry.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    _assert_owns_item(item, current_user, db)
    crud.expiry.delete_expiry_item(db, item=item)
    return {"message": "Item removed successfully"}
