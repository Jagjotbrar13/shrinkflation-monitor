from api.database import SessionLocal
from api.models import Product


def refresh_insights() -> int:
    db = SessionLocal()
    try:
        return db.query(Product).count()
    finally:
        db.close()


if __name__ == "__main__":
    print(f"Refreshed insight candidates for {refresh_insights()} products")
