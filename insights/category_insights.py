from collections import Counter

from api.models import ShrinkEvent
from api.schemas import InsightOut


def category_insights(events: list[ShrinkEvent]) -> list[InsightOut]:
    counts = Counter(event.product.category or "Uncategorized" for event in events)
    if not counts:
        return []
    category, count = counts.most_common(1)[0]
    return [
        InsightOut(
            title="Category pressure",
            body=f"{category} is currently the most affected tracked category with {count} events.",
            tone="warning",
        )
    ]
