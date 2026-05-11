from decimal import Decimal

from api.schemas import InsightOut


def basket_change_insights(change_pct: Decimal) -> list[InsightOut]:
    if change_pct > Decimal("0"):
        return [
            InsightOut(
                title="Basket cost",
                body=f"Your tracked basket is {change_pct}% more expensive than last week.",
                tone="warning",
            )
        ]
    if change_pct < Decimal("0"):
        return [
            InsightOut(
                title="Basket cost",
                body=f"Your tracked basket is {abs(change_pct)}% cheaper than last week.",
                tone="positive",
            )
        ]
    return [
        InsightOut(
            title="Basket cost",
            body="Your tracked basket is unchanged from last week.",
        )
    ]
