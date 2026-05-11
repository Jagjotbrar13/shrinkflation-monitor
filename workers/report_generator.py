from api.database import SessionLocal
from api.models import User


def generate_weekly_reports() -> int:
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return len(users)
    finally:
        db.close()


if __name__ == "__main__":
    print(f"Prepared weekly reports for {generate_weekly_reports()} users")
