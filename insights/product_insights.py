from decimal import Decimal

from api.models import Product, ShrinkEvent, Snapshot
from api.schemas import InsightOut


def product_insights(
    product: Product,
    snapshots: list[Snapshot],
    events: list[ShrinkEvent],
) -> list[InsightOut]:
    insights: list[InsightOut] = []
    if events:
        total_change = sum(
            ((event.ppu_change_pct or Decimal("0")) for event in events),
            Decimal("0"),
        )
        insights.append(
            InsightOut(
                title="Shrinkflation history",
                body=(
                    f"{product.name} has shrinkflated {len(events)} time"
                    f"{'' if len(events) == 1 else 's'}, raising unit price by "
                    f"{total_change.quantize(Decimal('0.01'))}% across tracked events."
                ),
                tone="warning",
            )
        )

    latest_by_store: dict[str, Snapshot] = {}
    for snapshot in sorted(snapshots, key=lambda item: item.scraped_at, reverse=True):
        latest_by_store.setdefault(snapshot.store, snapshot)

    priced = [
        snapshot
        for snapshot in latest_by_store.values()
        if snapshot.price_per_unit is not None and snapshot.unit_type is not None
    ]
    if priced:
        best = min(priced, key=lambda item: item.price_per_unit or Decimal("9999"))
        worst = max(priced, key=lambda item: item.price_per_unit or Decimal("0"))
        savings = Decimal("0.00")
        if worst.price_per_unit and best.price_per_unit and worst.price_per_unit > 0:
            savings = (
                (worst.price_per_unit - best.price_per_unit)
                / worst.price_per_unit
                * Decimal("100")
            ).quantize(Decimal("0.01"))
        body = (
            f"{best.store.title()} has the best tracked price at "
            f"${best.price_per_unit}/{best.unit_type}, about {savings}% below "
            "the worst store."
        )
        insights.append(
            InsightOut(
                title="Best current store",
                body=body,
                tone="positive",
            )
        )

    return insights
