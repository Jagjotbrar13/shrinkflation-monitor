import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from api.auth.demo import DEMO_USER_ID, DEMO_WATCHLIST_IDS
from api.auth.dependencies import get_current_user
from api.database import get_db
from api.demo_data import demo_product_detail
from api.models import Product, User, WatchlistItem
from api.schemas import ProductOut, WatchlistItemOut

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=list[WatchlistItemOut])
def get_watchlist(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[WatchlistItemOut]:
    if user.id == DEMO_USER_ID:
        return _demo_watchlist()
    try:
        items = (
            db.query(WatchlistItem)
            .options(joinedload(WatchlistItem.product))
            .filter(WatchlistItem.user_id == user.id)
            .order_by(WatchlistItem.added_at.desc())
            .all()
        )
        return [
            WatchlistItemOut(
                id=item.id,
                product=ProductOut.model_validate(item.product),
                added_at=item.added_at,
            )
            for item in items
        ]
    except SQLAlchemyError:
        return _demo_watchlist()


@router.post("/{product_id}", response_model=WatchlistItemOut, status_code=status.HTTP_201_CREATED)
def add_watchlist_item(
    product_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WatchlistItemOut:
    if user.id == DEMO_USER_ID:
        demo = demo_product_detail(product_id)
        if not demo:
            raise HTTPException(status_code=404, detail="Product not found")
        return WatchlistItemOut(
            id=uuid.uuid5(uuid.NAMESPACE_URL, f"demo-watchlist:{product_id}"),
            product=ProductOut.model_validate(demo),
            added_at=datetime.now(UTC),
        )

    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == user.id, WatchlistItem.product_id == product_id)
        .one_or_none()
    )
    if existing:
        return WatchlistItemOut(
            id=existing.id,
            product=ProductOut.model_validate(product),
            added_at=existing.added_at,
        )

    item = WatchlistItem(user_id=user.id, product_id=product_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return WatchlistItemOut(
        id=item.id,
        product=ProductOut.model_validate(product),
        added_at=item.added_at,
    )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_watchlist_item(
    product_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if user.id == DEMO_USER_ID:
        return
    item = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == user.id, WatchlistItem.product_id == product_id)
        .one_or_none()
    )
    if item:
        db.delete(item)
        db.commit()


def _demo_watchlist() -> list[WatchlistItemOut]:
    items: list[WatchlistItemOut] = []
    now = datetime.now(UTC)
    for index, product_id in enumerate(DEMO_WATCHLIST_IDS):
        detail = demo_product_detail(product_id)
        if detail:
            items.append(
                WatchlistItemOut(
                    id=uuid.uuid5(uuid.NAMESPACE_URL, f"demo-watchlist:{product_id}"),
                    product=ProductOut.model_validate(detail),
                    added_at=now - timedelta(days=index + 1),
                )
            )
    return items
