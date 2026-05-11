import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from api.database import get_db
from api.demo_data import demo_product_detail, demo_products, demo_snapshots
from api.models import Product, ShrinkEvent, Snapshot
from api.routes._helpers import event_to_schema, latest_snapshots_for_product
from api.schemas import ProductDetailOut, ProductOut, SnapshotOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(
    q: str | None = Query(default=None),
    category: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[ProductOut]:
    try:
        query = db.query(Product).order_by(Product.name.asc())
        if q:
            like = f"%{q}%"
            query = query.filter(or_(Product.name.ilike(like), Product.brand.ilike(like)))
        if category:
            query = query.filter(Product.category == category)
        products = query.limit(limit).all()
        return [ProductOut.model_validate(product) for product in products] or demo_products()
    except SQLAlchemyError:
        return demo_products()


@router.get("/{product_id}", response_model=ProductDetailOut)
def get_product(product_id: uuid.UUID, db: Session = Depends(get_db)) -> ProductDetailOut:
    try:
        product = db.get(Product, product_id)
    except SQLAlchemyError:
        product = None
    if not product:
        demo = demo_product_detail(product_id)
        if demo:
            return demo
        raise HTTPException(status_code=404, detail="Product not found")

    events = (
        db.query(ShrinkEvent)
        .options(joinedload(ShrinkEvent.product))
        .filter(ShrinkEvent.product_id == product_id)
        .order_by(ShrinkEvent.detected_at.desc())
        .all()
    )
    return ProductDetailOut(
        **ProductOut.model_validate(product).model_dump(),
        latest_snapshots=[
            SnapshotOut.model_validate(snapshot)
            for snapshot in latest_snapshots_for_product(db, product_id)
        ],
        shrink_events=[event_to_schema(event) for event in events],
    )


@router.get("/{product_id}/history", response_model=list[SnapshotOut])
def product_history(
    product_id: uuid.UUID,
    store: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[SnapshotOut]:
    try:
        query = db.query(Snapshot).filter(Snapshot.product_id == product_id)
        if store:
            query = query.filter(Snapshot.store == store.lower())
        snapshots = query.order_by(Snapshot.scraped_at.asc()).all()
        return [SnapshotOut.model_validate(snapshot) for snapshot in snapshots] or demo_snapshots(
            product_id
        )
    except SQLAlchemyError:
        return demo_snapshots(product_id)
