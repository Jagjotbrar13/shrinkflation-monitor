import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from api.database import get_db
from api.demo_data import demo_product_detail, demo_product_insights
from api.models import Product, ShrinkEvent
from api.routes._helpers import latest_snapshots_for_product
from api.schemas import InsightOut
from insights.category_insights import category_insights
from insights.product_insights import product_insights
from insights.store_insights import store_ranking_insights

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/product/{product_id}", response_model=list[InsightOut])
def product_level_insights(
    product_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[InsightOut]:
    try:
        product = db.get(Product, product_id)
    except SQLAlchemyError:
        product = None
    if not product:
        if demo_product_detail(product_id):
            return demo_product_insights(product_id)
        raise HTTPException(status_code=404, detail="Product not found")
    snapshots = latest_snapshots_for_product(db, product_id)
    events = (
        db.query(ShrinkEvent)
        .options(joinedload(ShrinkEvent.product))
        .filter(ShrinkEvent.product_id == product_id)
        .order_by(ShrinkEvent.detected_at.desc())
        .all()
    )
    return product_insights(product, snapshots, events)


@router.get("/stores", response_model=list[InsightOut])
def store_level_insights(db: Session = Depends(get_db)) -> list[InsightOut]:
    since = datetime.now(UTC) - timedelta(days=31)
    try:
        events = db.query(ShrinkEvent).filter(ShrinkEvent.detected_at >= since).all()
    except SQLAlchemyError:
        events = []
    return store_ranking_insights(events)


@router.get("/categories", response_model=list[InsightOut])
def category_level_insights(db: Session = Depends(get_db)) -> list[InsightOut]:
    since = datetime.now(UTC) - timedelta(days=31)
    try:
        events = (
            db.query(ShrinkEvent)
            .options(joinedload(ShrinkEvent.product))
            .filter(ShrinkEvent.detected_at >= since)
            .all()
        )
    except SQLAlchemyError:
        events = []
    return category_insights(events)
