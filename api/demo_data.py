from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from api.schemas import (
    CategoryRollupOut,
    InsightOut,
    ProductDetailOut,
    ProductOut,
    ShrinkEventOut,
    SnapshotOut,
    StoreComparisonOut,
)

DEMO_ITEMS = [
    (
        "Maple Crunch Cereal",
        "Kellogg's",
        "Pantry",
        "Cereal",
        "walmart",
        "500",
        "450",
        "4.99",
        "4.99",
    ),
    (
        "Creamy Peanut Butter",
        "Kraft",
        "Pantry",
        "Spreads",
        "loblaws",
        "1000",
        "850",
        "6.49",
        "6.79",
    ),
    ("Classic Potato Chips", "Lay's", "Snacks", "Chips", "sobeys", "235", "200", "4.29", "4.29"),
    ("Greek Yogurt Tub", "Oikos", "Dairy", "Yogurt", "save-on", "750", "650", "6.99", "6.99"),
    ("Ground Coffee", "Tim Hortons", "Pantry", "Coffee", "walmart", "340", "300", "9.99", "10.49"),
    ("Granola Bars", "Nature Valley", "Snacks", "Bars", "loblaws", "240", "210", "3.99", "3.99"),
    (
        "Frozen Pepperoni Pizza",
        "Dr. Oetker",
        "Frozen",
        "Pizza",
        "sobeys",
        "390",
        "340",
        "5.99",
        "5.99",
    ),
    (
        "Cheddar Cheese Block",
        "Cracker Barrel",
        "Dairy",
        "Cheese",
        "save-on",
        "600",
        "550",
        "8.99",
        "9.49",
    ),
    (
        "Chocolate Sandwich Cookies",
        "Oreo",
        "Snacks",
        "Cookies",
        "walmart",
        "303",
        "270",
        "3.79",
        "3.79",
    ),
    ("Pasta Sauce", "Classico", "Pantry", "Sauces", "loblaws", "650", "600", "4.49", "4.79"),
    ("Frozen Fries", "McCain", "Frozen", "Potatoes", "sobeys", "900", "750", "4.99", "4.99"),
    ("Chicken Nuggets", "Jane's", "Frozen", "Chicken", "save-on", "700", "600", "11.99", "12.49"),
    ("Instant Oatmeal", "Quaker", "Pantry", "Breakfast", "walmart", "430", "360", "4.29", "4.49"),
    ("Trail Mix", "Kirkland", "Snacks", "Nuts", "loblaws", "900", "750", "13.99", "13.99"),
    ("Ice Cream Tub", "Chapman's", "Frozen", "Dessert", "sobeys", "2000", "1650", "6.49", "6.99"),
    ("Butter Sticks", "Lactantia", "Dairy", "Butter", "save-on", "454", "400", "6.99", "7.29"),
    ("Canned Soup", "Campbell's", "Pantry", "Soup", "walmart", "540", "515", "2.49", "2.49"),
    ("Pancake Mix", "Aunt Jemima", "Pantry", "Baking", "loblaws", "905", "800", "5.49", "5.79"),
    ("Ranch Dressing", "Kraft", "Pantry", "Condiments", "sobeys", "475", "425", "4.19", "4.19"),
    (
        "Chocolate Bar Pack",
        "KitKat",
        "Snacks",
        "Chocolate",
        "save-on",
        "180",
        "150",
        "5.99",
        "5.99",
    ),
    (
        "Dishwasher Pods",
        "Cascade",
        "Household",
        "Cleaning",
        "walmart",
        "650",
        "560",
        "18.99",
        "19.99",
    ),
    (
        "Laundry Detergent",
        "Tide",
        "Household",
        "Laundry",
        "loblaws",
        "1700",
        "1500",
        "17.99",
        "18.49",
    ),
    (
        "Shampoo Bottle",
        "Dove",
        "Personal Care",
        "Hair Care",
        "sobeys",
        "355",
        "320",
        "6.99",
        "6.99",
    ),
    (
        "Toothpaste",
        "Colgate",
        "Personal Care",
        "Oral Care",
        "save-on",
        "130",
        "110",
        "3.49",
        "3.79",
    ),
    ("Baby Wipes", "Pampers", "Baby", "Wipes", "walmart", "1000", "840", "22.99", "22.99"),
    ("Apple Juice", "Allen's", "Beverages", "Juice", "loblaws", "2000", "1750", "3.99", "4.19"),
    (
        "Sparkling Water Pack",
        "Bubly",
        "Beverages",
        "Water",
        "sobeys",
        "4260",
        "3840",
        "6.99",
        "7.49",
    ),
    ("Protein Bars", "Clif", "Snacks", "Bars", "save-on", "408", "340", "11.99", "12.49"),
]


def demo_products() -> list[ProductOut]:
    return [
        ProductOut(
            id=_product_id(index),
            barcode=f"06038312{index:04d}",
            name=item[0],
            brand=item[1],
            category=item[2],
            subcategory=item[3],
        )
        for index, item in enumerate(DEMO_ITEMS, start=1)
    ]


def demo_snapshots(product_id: UUID | None = None) -> list[SnapshotOut]:
    now = datetime.now(UTC)
    rows: list[SnapshotOut] = []
    for index, item in enumerate(DEMO_ITEMS, start=1):
        old_date = now - timedelta(days=35 + index * 2)
        new_date = now - timedelta(days=index % 11)
        rows.append(_snapshot(index, item, old_date, old=True))
        rows.append(_snapshot(index, item, new_date, old=False))
    if product_id:
        return [row for row in rows if row.product_id == product_id]
    return rows


def demo_events() -> list[ShrinkEventOut]:
    now = datetime.now(UTC)
    events: list[ShrinkEventOut] = []
    for index, item in enumerate(DEMO_ITEMS, start=1):
        old_ppu = _ppu(item[7], item[5])
        new_ppu = _ppu(item[8], item[6])
        ppu_change = _pct_change(old_ppu, new_ppu)
        events.append(
            ShrinkEventOut(
                id=_event_id(index),
                product_id=_product_id(index),
                product_name=item[0],
                brand=item[1],
                category=item[2],
                store=item[4],
                detected_at=now - timedelta(days=index % 11),
                old_weight_g=Decimal(item[5]),
                new_weight_g=Decimal(item[6]),
                old_price=Decimal(item[7]),
                new_price=Decimal(item[8]),
                old_ppu=old_ppu,
                new_ppu=new_ppu,
                ppu_change_pct=ppu_change,
                severity=_severity(ppu_change),
            )
        )
    return sorted(events, key=lambda event: event.ppu_change_pct or Decimal("0"), reverse=True)


def demo_product_detail(product_id: UUID) -> ProductDetailOut | None:
    product = next((item for item in demo_products() if item.id == product_id), None)
    if not product:
        return None
    snapshots = demo_snapshots(product_id)
    return ProductDetailOut(
        **product.model_dump(),
        latest_snapshots=snapshots[-2:],
        shrink_events=[event for event in demo_events() if event.product_id == product_id],
    )


def demo_product_insights(product_id: UUID) -> list[InsightOut]:
    detail = demo_product_detail(product_id)
    if not detail:
        return []
    event = detail.shrink_events[0] if detail.shrink_events else None
    if not event or not event.ppu_change_pct:
        return []
    return [
        InsightOut(
            title="Shrinkflation history",
            body=(
                f"{detail.name} shrank from {event.old_weight_g}g to {event.new_weight_g}g, "
                f"raising unit price by {event.ppu_change_pct}%."
            ),
            tone="warning",
        ),
        InsightOut(
            title="Store signal",
            body=(
                f"{event.store.title()} is currently the tracked store for this change, "
                f"with severity marked {event.severity}."
            ),
            tone="neutral",
        ),
    ]


def demo_store_comparison() -> list[StoreComparisonOut]:
    grouped: dict[str, list[ShrinkEventOut]] = defaultdict(list)
    for event in demo_events():
        grouped[event.store].append(event)
    rows = []
    for store, events in grouped.items():
        average = (
            sum((event.new_ppu or Decimal("0") for event in events), Decimal("0"))
            / Decimal(len(events))
        ).quantize(Decimal("0.0001"))
        rows.append(
            StoreComparisonOut(
                store=store,
                average_price_per_unit=average,
                products_tracked=len(events),
            )
        )
    return sorted(rows, key=lambda row: row.products_tracked, reverse=True)


def demo_category_rollup() -> list[CategoryRollupOut]:
    counts = Counter(event.category or "Uncategorized" for event in demo_events())
    return [
        CategoryRollupOut(
            category=category,
            event_count=count,
            average_ppu_change_pct=_category_average(category),
        )
        for category, count in counts.most_common()
    ]


def _snapshot(index: int, item: tuple[str, ...], scraped_at: datetime, *, old: bool) -> SnapshotOut:
    size = item[5] if old else item[6]
    price = item[7] if old else item[8]
    return SnapshotOut(
        id=UUID(int=10_000 + index * 2 + (0 if old else 1)),
        product_id=_product_id(index),
        store=item[4],
        location="edmonton",
        price=Decimal(price),
        weight_g=Decimal(size),
        volume_ml=None,
        price_per_unit=_ppu(price, size),
        unit_type="100g",
        scraped_at=scraped_at,
    )


def _product_id(index: int) -> UUID:
    return UUID(int=index)


def _event_id(index: int) -> UUID:
    return UUID(int=50_000 + index)


def _ppu(price: str, grams: str) -> Decimal:
    return (Decimal(price) / Decimal(grams) * Decimal("100")).quantize(Decimal("0.0001"))


def _pct_change(old: Decimal, new: Decimal) -> Decimal:
    return ((new - old) / old * Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def _severity(ppu_change: Decimal) -> str:
    if ppu_change >= Decimal("25"):
        return "critical"
    if ppu_change >= Decimal("15"):
        return "high"
    if ppu_change >= Decimal("8"):
        return "moderate"
    return "low"


def _category_average(category: str) -> Decimal:
    events = [event for event in demo_events() if event.category == category]
    return (
        sum((event.ppu_change_pct or Decimal("0") for event in events), Decimal("0"))
        / Decimal(len(events))
    ).quantize(Decimal("0.01"))
