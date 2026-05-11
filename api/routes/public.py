from collections import defaultdict
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from api.database import get_db
from api.demo_data import demo_category_rollup, demo_events, demo_store_comparison
from api.models import ShrinkEvent, Snapshot
from api.routes._helpers import event_to_schema
from api.schemas import CategoryRollupOut, ShrinkEventOut, StoreComparisonOut

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/leaderboard", response_model=list[ShrinkEventOut])
def leaderboard(
    limit: int = Query(default=25, ge=1, le=100),
    location: str | None = Query(default=None),
    store: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ShrinkEventOut]:
    try:
        query = db.query(ShrinkEvent).options(joinedload(ShrinkEvent.product))
        if store:
            query = query.filter(ShrinkEvent.store == store.lower())

        events = query.order_by(
            ShrinkEvent.ppu_change_pct.desc().nullslast(), ShrinkEvent.detected_at.desc()
        ).limit(limit).all()
        if not events:
            return demo_events()[:limit]
        if location:
            events = [event for event in events if event.product.snapshots]
        return [event_to_schema(event) for event in events]
    except SQLAlchemyError:
        return demo_events()[:limit]


@router.get("/stores/comparison", response_model=list[StoreComparisonOut])
def store_comparison(db: Session = Depends(get_db)) -> list[StoreComparisonOut]:
    try:
        snapshots = db.query(Snapshot).filter(Snapshot.price_per_unit.isnot(None)).all()
    except SQLAlchemyError:
        return demo_store_comparison()
    if not snapshots:
        return demo_store_comparison()
    totals: dict[str, list[Decimal]] = defaultdict(list)
    for snapshot in snapshots:
        if snapshot.price_per_unit is not None:
            totals[snapshot.store].append(snapshot.price_per_unit)

    rows: list[StoreComparisonOut] = []
    for store, values in totals.items():
        average = (sum(values, Decimal("0")) / len(values)).quantize(Decimal("0.0001"))
        rows.append(
            StoreComparisonOut(
                store=store,
                average_price_per_unit=average,
                products_tracked=len(values),
            )
        )
    return sorted(rows, key=lambda item: item.average_price_per_unit)


@router.get("/categories/rollup", response_model=list[CategoryRollupOut])
def category_rollup(db: Session = Depends(get_db)) -> list[CategoryRollupOut]:
    try:
        events = db.query(ShrinkEvent).options(joinedload(ShrinkEvent.product)).all()
    except SQLAlchemyError:
        return demo_category_rollup()
    if not events:
        return demo_category_rollup()
    grouped: dict[str, list[ShrinkEvent]] = defaultdict(list)
    for event in events:
        grouped[event.product.category or "Uncategorized"].append(event)

    rows: list[CategoryRollupOut] = []
    for category, category_events in grouped.items():
        total = sum(
            ((event.ppu_change_pct or Decimal("0")) for event in category_events),
            Decimal("0"),
        )
        avg_change = (total / Decimal(len(category_events))).quantize(Decimal("0.01"))
        rows.append(
            CategoryRollupOut(
                category=category,
                event_count=len(category_events),
                average_ppu_change_pct=avg_change,
            )
        )
    return sorted(rows, key=lambda item: item.event_count, reverse=True)
