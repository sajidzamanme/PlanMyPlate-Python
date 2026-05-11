from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date


# ── Request DTOs ──────────────────────────────────────────────────────────────

class ExpiryEntryRequest(BaseModel):
    """
    Body for POST /expiry/user/{user_id}/items
    The user provides a product name (free text) and the expiry date.
    If the product name matches an existing ingredient it is reused;
    otherwise a new ingredient row is created automatically.
    """
    productName: str = Field(..., min_length=1, max_length=150, alias="product_name")
    expiryDate: date = Field(..., alias="expiry_date")
    quantity: float = Field(default=1.0, gt=0)
    unit: str = Field(default="unit", max_length=50)

    model_config = {"populate_by_name": True}


class ExpiryItemUpdateRequest(BaseModel):
    """Body for PUT /expiry/items/{item_id} — all fields optional (partial update)."""
    expiryDate: Optional[date] = Field(None, alias="expiry_date")
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=50)

    model_config = {"populate_by_name": True}


# ── Response DTOs ─────────────────────────────────────────────────────────────

class ExpiryItemResponse(BaseModel):
    """
    A single inventory item enriched with computed expiry-related fields.
    Uses the existing InvItem model; adds daysUntilExpiry and isExpired.
    """
    itemId: int             = Field(alias="item_id")
    productName: str        = Field(alias="product_name")   # ingredient name
    expiryDate: Optional[date] = Field(None, alias="expiry_date")
    dateAdded: Optional[date]  = Field(None, alias="date_added")
    quantity: Optional[float]  = None
    unit: Optional[str]        = None
    daysUntilExpiry: Optional[int] = None  # computed: None when no expiry_date
    isExpired: bool            = False      # computed

    model_config = {"from_attributes": True, "populate_by_name": True}


class SoonToExpireResponse(BaseModel):
    """Wrapper returned by GET /expiry/user/{user_id}/soon"""
    thresholdDays: int
    totalCount: int
    expiredCount: int                       # items with expiry_date < today
    items: List[ExpiryItemResponse]
