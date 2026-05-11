from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from api.auth.dependencies import get_current_user
from api.database import get_db
from api.models import Alert, ShrinkEvent, User
from api.routes._helpers import event_to_schema
from api.schemas import AlertOut, ProductOut

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[AlertOut]:
    alerts = (
        db.query(Alert)
        .options(
            joinedload(Alert.product),
            joinedload(Alert.shrink_event).joinedload(ShrinkEvent.product),
        )
        .filter(Alert.user_id == user.id)
        .order_by(Alert.sent_at.desc())
        .all()
    )
    return [
        AlertOut(
            id=alert.id,
            product=ProductOut.model_validate(alert.product),
            shrink_event=event_to_schema(alert.shrink_event),
            sent_at=alert.sent_at,
            channel=alert.channel,
        )
        for alert in alerts
    ]
