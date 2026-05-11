import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from api.models import ShrinkEvent, Snapshot
from api.schemas import ShrinkEventOut


def event_to_schema(event: ShrinkEvent) -> ShrinkEventOut:
    product = event.product
    return ShrinkEventOut(
        id=event.id,
        product_id=event.product_id,
        product_name=product.name,
        brand=product.brand,
        category=product.category,
        store=event.store,
        detected_at=event.detected_at,
        old_weight_g=event.old_weight_g,
        new_weight_g=event.new_weight_g,
        old_price=event.old_price,
        new_price=event.new_price,
        old_ppu=event.old_ppu,
        new_ppu=event.new_ppu,
        ppu_change_pct=event.ppu_change_pct,
        severity=event.severity,
    )


def latest_snapshots_for_product(db: Session, product_id: uuid.UUID) -> list[Snapshot]:
    snapshots = (
        db.query(Snapshot)
        .filter(Snapshot.product_id == product_id)
        .order_by(Snapshot.store.asc(), Snapshot.scraped_at.desc())
        .all()
    )
    latest_by_store: dict[str, Snapshot] = {}
    for snapshot in snapshots:
        latest_by_store.setdefault(snapshot.store, snapshot)
    return list(latest_by_store.values())


def pct_change(old: Decimal, new: Decimal) -> Decimal:
    if old <= 0:
        return Decimal("0.00")
    return ((new - old) / old * Decimal("100")).quantize(Decimal("0.01"))
