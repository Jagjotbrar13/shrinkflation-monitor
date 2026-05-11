import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProductOut(BaseModel):
    id: uuid.UUID
    barcode: str | None
    name: str
    brand: str | None
    category: str | None
    subcategory: str | None

    model_config = ConfigDict(from_attributes=True)


class SnapshotOut(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    store: str
    location: str | None
    price: Decimal
    weight_g: Decimal | None
    volume_ml: Decimal | None
    price_per_unit: Decimal | None
    unit_type: str | None
    scraped_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ShrinkEventOut(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    brand: str | None
    category: str | None
    store: str
    detected_at: datetime
    old_weight_g: Decimal | None
    new_weight_g: Decimal | None
    old_price: Decimal
    new_price: Decimal
    old_ppu: Decimal | None
    new_ppu: Decimal | None
    ppu_change_pct: Decimal | None
    severity: str


class ProductDetailOut(ProductOut):
    latest_snapshots: list[SnapshotOut]
    shrink_events: list[ShrinkEventOut]


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    location: str = "edmonton"
    preferred_stores: list[str] | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    location: str
    preferred_stores: list[str] | None

    model_config = ConfigDict(from_attributes=True)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class WatchlistItemOut(BaseModel):
    id: uuid.UUID
    product: ProductOut
    added_at: datetime


class AlertOut(BaseModel):
    id: uuid.UUID
    product: ProductOut
    shrink_event: ShrinkEventOut
    sent_at: datetime
    channel: str


class InsightOut(BaseModel):
    title: str
    body: str
    tone: str = "neutral"


class BasketReportOut(BaseModel):
    user_id: uuid.UUID
    week: str
    tracked_products: int
    current_cost: Decimal
    previous_cost: Decimal
    change_pct: Decimal
    insights: list[InsightOut]


class StoreComparisonOut(BaseModel):
    store: str
    average_price_per_unit: Decimal
    products_tracked: int


class CategoryRollupOut(BaseModel):
    category: str
    event_count: int
    average_ppu_change_pct: Decimal
