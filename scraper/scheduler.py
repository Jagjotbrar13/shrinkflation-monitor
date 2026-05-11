from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models import Product, ShrinkEvent, Snapshot
from scraper.detector import SnapshotRecord, detect_shrink_event
from scraper.normalizer import ProductObservation
from scraper.seed_demo_data import DEMO_SERIES


def run_daily_pipeline() -> int:
    observations = _demo_observations()
    db = SessionLocal()
    try:
        inserted = persist_observations(db, observations)
        db.commit()
        return inserted
    finally:
        db.close()


def persist_observations(db: Session, observations: list[ProductObservation]) -> int:
    inserted = 0
    for observation in observations:
        product = _get_or_create_product(db, observation)
        previous_snapshot = (
            db.query(Snapshot)
            .filter(Snapshot.product_id == product.id, Snapshot.store == observation.store)
            .order_by(Snapshot.scraped_at.desc())
            .first()
        )
        snapshot = Snapshot(
            product_id=product.id,
            store=observation.store,
            location=observation.location,
            price=observation.price,
            weight_g=observation.weight_g,
            volume_ml=observation.volume_ml,
            price_per_unit=observation.price_per_unit,
            unit_type=observation.unit_type,
        )
        db.add(snapshot)
        db.flush()
        inserted += 1

        if previous_snapshot:
            event = detect_shrink_event(
                SnapshotRecord(
                    product_id=str(product.id),
                    store=previous_snapshot.store,
                    price=previous_snapshot.price,
                    weight_g=previous_snapshot.weight_g,
                    price_per_unit=previous_snapshot.price_per_unit,
                    unit_type=previous_snapshot.unit_type,
                ),
                SnapshotRecord(
                    product_id=str(product.id),
                    store=snapshot.store,
                    price=snapshot.price,
                    weight_g=snapshot.weight_g,
                    price_per_unit=snapshot.price_per_unit,
                    unit_type=snapshot.unit_type,
                ),
            )
            if event:
                db.add(
                    ShrinkEvent(
                        product_id=product.id,
                        store=event.store,
                        old_weight_g=event.old_weight_g,
                        new_weight_g=event.new_weight_g,
                        old_price=event.old_price,
                        new_price=event.new_price,
                        old_ppu=event.old_ppu,
                        new_ppu=event.new_ppu,
                        ppu_change_pct=event.ppu_change_pct,
                        severity=event.severity,
                    )
                )
    return inserted


def _get_or_create_product(db: Session, observation: ProductObservation) -> Product:
    product = None
    if observation.barcode:
        product = db.query(Product).filter(Product.barcode == observation.barcode).one_or_none()
    if product:
        return product
    product = Product(
        barcode=observation.barcode,
        name=observation.name,
        brand=observation.brand,
        category=observation.category,
        subcategory=observation.subcategory,
    )
    db.add(product)
    db.flush()
    return product


def _demo_observations() -> list[ProductObservation]:
    from scraper.normalizer import normalize_observation

    observations: list[ProductObservation] = []
    for item in DEMO_SERIES:
        observations.append(
            normalize_observation(
                barcode=str(item["barcode"]),
                name=str(item["name"]),
                brand=str(item["brand"]),
                category=str(item["category"]),
                store=str(item["store"]),
                price=str(item["prices"][-1]),
                package_size=str(item["sizes"][-1]),
            )
        )
    return observations


if __name__ == "__main__":
    count = run_daily_pipeline()
    print(f"Inserted {count} snapshots")
