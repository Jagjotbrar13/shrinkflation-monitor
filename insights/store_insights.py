from collections import Counter

from api.models import ShrinkEvent
from api.schemas import InsightOut


def store_ranking_insights(events: list[ShrinkEvent]) -> list[InsightOut]:
    counts = Counter(event.store for event in events)
    if not counts:
        return [
            InsightOut(
                title="Store ranking",
                body="No shrinkflation events have been detected for the selected stores yet.",
            )
        ]
    store, count = counts.most_common(1)[0]
    return [
        InsightOut(
            title="Store ranking",
            body=(
                f"{store.title()} has the most tracked shrinkflation events "
                f"this month with {count}."
            ),
            tone="warning",
        )
    ]
