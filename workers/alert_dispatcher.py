from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models import Alert, ShrinkEvent, WatchlistItem


def dispatch_pending_alerts() -> int:
    db = SessionLocal()
    try:
        count = dispatch_pending_alerts_for_db(db)
        db.commit()
        return count
    finally:
        db.close()


def dispatch_pending_alerts_for_db(db: Session) -> int:
    count = 0
    events = db.query(ShrinkEvent).order_by(ShrinkEvent.detected_at.desc()).limit(100).all()
    for event in events:
        watchers = (
            db.query(WatchlistItem)
            .filter(WatchlistItem.product_id == event.product_id)
            .all()
        )
        for watcher in watchers:
            existing = (
                db.query(Alert)
                .filter(Alert.user_id == watcher.user_id, Alert.shrink_event_id == event.id)
                .one_or_none()
            )
            if existing:
                continue
            db.add(
                Alert(
                    user_id=watcher.user_id,
                    product_id=event.product_id,
                    shrink_event_id=event.id,
                    channel="email",
                )
            )
            count += 1
    return count


if __name__ == "__main__":
    print(f"Created {dispatch_pending_alerts()} alerts")
