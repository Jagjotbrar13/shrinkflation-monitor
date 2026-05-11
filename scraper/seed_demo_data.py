from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models import Product, ShrinkEvent, Snapshot
from scraper.detector import SnapshotRecord, detect_shrink_event
from scraper.normalizer import normalize_observation

DEMO_SERIES = [
    {
        "barcode": "060383123451",
        "name": "Maple Crunch Cereal",
        "brand": "Northern Pantry",
        "category": "Pantry",
        "store": "walmart",
        "sizes": ["500 g", "450 g"],
        "prices": ["$4.99", "$4.99"],
    },
    {
        "barcode": "060383123452",
        "name": "Creamy Peanut Butter",
        "brand": "Prairie Choice",
        "category": "Pantry",
        "store": "loblaws",
        "sizes": ["1 kg", "850 g"],
        "prices": ["$6.49", "$6.79"],
    },
    {
        "barcode": "060383123453",
        "name": "Family Pasta Sauce",
        "brand": "Kitchen Table",
        "category": "Pantry",
        "store": "save-on",
        "sizes": ["700 ml", "650 ml"],
        "prices": ["$3.79", "$3.49"],
    },
]


def upsert_product(db: Session, item: dict[str, str | list[str]]) -> Product:
    product = db.query(Product).filter(Product.barcode == item["barcode"]).one_or_none()
    if product:
        return product

    product = Product(
        barcode=str(item["barcode"]),
        name=str(item["name"]),
        brand=str(item["brand"]),
        category=str(item["category"]),
    )
    db.add(product)
    db.flush()
    return product


def seed() -> None:
    db = SessionLocal()
    try:
        for item in DEMO_SERIES:
            product = upsert_product(db, item)
            if product.snapshots:
                continue
            previous_record: SnapshotRecord | None = None
            base_time = datetime.now(UTC) - timedelta(days=45)

            for index, (size, price) in enumerate(zip(item["sizes"], item["prices"], strict=True)):
                observation = normalize_observation(
                    barcode=str(item["barcode"]),
                    name=str(item["name"]),
                    brand=str(item["brand"]),
                    category=str(item["category"]),
                    store=str(item["store"]),
                    price=str(price),
                    package_size=str(size),
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
                    scraped_at=base_time + timedelta(days=index * 45),
                )
                db.add(snapshot)
                db.flush()

                current_record = SnapshotRecord(
                    product_id=str(product.id),
                    store=snapshot.store,
                    price=Decimal(snapshot.price),
                    weight_g=Decimal(snapshot.weight_g) if snapshot.weight_g is not None else None,
                    price_per_unit=Decimal(snapshot.price_per_unit)
                    if snapshot.price_per_unit is not None
                    else None,
                    unit_type=snapshot.unit_type,
                )
                if previous_record:
                    event = detect_shrink_event(previous_record, current_record)
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
                previous_record = current_record

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
