from uuid import UUID

from api.models import User

DEMO_USER_ID = UUID("99999999-9999-4999-8999-999999999999")
DEMO_EMAIL = "demo@grocerydemo.com"
DEMO_PASSWORD = "password123"
DEMO_WATCHLIST_IDS = [
    UUID(int=15),
    UUID(int=2),
    UUID(int=5),
    UUID(int=21),
    UUID(int=26),
]


def demo_user_model() -> User:
    return User(
        id=DEMO_USER_ID,
        email=DEMO_EMAIL,
        password_hash="demo-account",
        location="edmonton",
        preferred_stores=["walmart", "loblaws", "sobeys", "save-on"],
    )
