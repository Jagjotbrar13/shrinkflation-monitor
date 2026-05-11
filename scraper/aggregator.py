from collections.abc import Iterable

from scraper.detector import ShrinkEventCandidate, SnapshotRecord, detect_shrink_event


def detect_events_for_series(snapshots: Iterable[SnapshotRecord]) -> list[ShrinkEventCandidate]:
    ordered = list(snapshots)
    events: list[ShrinkEventCandidate] = []
    for previous, current in zip(ordered, ordered[1:], strict=False):
        event = detect_shrink_event(previous, current)
        if event:
            events.append(event)
    return events
