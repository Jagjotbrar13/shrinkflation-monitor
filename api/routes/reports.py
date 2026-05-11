from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from api.auth.demo import DEMO_USER_ID, DEMO_WATCHLIST_IDS
from api.auth.dependencies import get_current_user
from api.database import get_db
from api.demo_data import demo_snapshots
from api.models import Snapshot, User, WatchlistItem
from api.schemas import BasketReportOut, SnapshotOut
from insights.basket_insights import basket_change_insights

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/weekly", response_model=BasketReportOut)
def weekly_report(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> BasketReportOut:
    if user.id == DEMO_USER_ID:
        return _demo_report(user)

    try:
        watchlist = (
            db.query(WatchlistItem)
            .options(joinedload(WatchlistItem.product))
            .filter(WatchlistItem.user_id == user.id)
            .all()
        )
    except SQLAlchemyError:
        return _demo_report(user)
    product_ids = [item.product_id for item in watchlist]
    snapshots = (
        db.query(Snapshot)
        .filter(Snapshot.product_id.in_(product_ids))
        .order_by(Snapshot.product_id.asc(), Snapshot.scraped_at.desc())
        .all()
        if product_ids
        else []
    )
    return _build_report(user, len(product_ids), snapshots)


def _demo_report(user: User) -> BasketReportOut:
    snapshots = []
    for product_id in DEMO_WATCHLIST_IDS:
        snapshots.extend(demo_snapshots(product_id))
    return _build_report(user, len(DEMO_WATCHLIST_IDS), snapshots)


def _build_report(
    user: User,
    tracked_products: int,
    snapshots: Sequence[Snapshot | SnapshotOut],
) -> BasketReportOut:
    latest: dict[object, Snapshot | SnapshotOut] = {}
    previous: dict[object, Snapshot | SnapshotOut] = {}
    for snapshot in sorted(snapshots, key=lambda item: item.scraped_at, reverse=True):
        if snapshot.product_id not in latest:
            latest[snapshot.product_id] = snapshot
        elif snapshot.product_id not in previous:
            previous[snapshot.product_id] = snapshot

    current_cost = sum((snapshot.price for snapshot in latest.values()), Decimal("0.00"))
    previous_cost = sum((snapshot.price for snapshot in previous.values()), Decimal("0.00"))
    change_pct = Decimal("0.00")
    if previous_cost > 0:
        change_pct = ((current_cost - previous_cost) / previous_cost * Decimal("100")).quantize(
            Decimal("0.01")
        )

    return BasketReportOut(
        user_id=user.id,
        week=datetime.now(UTC).strftime("%G-W%V"),
        tracked_products=tracked_products,
        current_cost=current_cost.quantize(Decimal("0.01")),
        previous_cost=previous_cost.quantize(Decimal("0.01")),
        change_pct=change_pct,
        insights=basket_change_insights(change_pct),
    )
