from app.database import SessionLocal, engine
from app.models import Contact
from sqlalchemy.orm import Session


# Optional: clear all data before seeding (for clean reruns)
def reset_db(db: Session):
    db.query(Contact).delete()
    db.commit()


def seed_contacts():
    db = SessionLocal()
    reset_db(db)

    contacts = [
        # Primary contact 1
        Contact(
            email="alice@example.com",
            phoneNumber="1234567890",
            linkPrecedence="primary",
        ),
        # Secondary contact (same phone as Alice)
        Contact(
            email="ali.c@example.com",
            phoneNumber="1234567890",
            linkPrecedence="secondary",
            linkedId=1,
        ),
        # Completely unrelated contact
        Contact(
            email="bob@example.com", phoneNumber="9876543210", linkPrecedence="primary"
        ),
        # Secondary contact (same email as Bob)
        Contact(
            email="bob@example.com",
            phoneNumber="1112223333",
            linkPrecedence="secondary",
            linkedId=3,
        ),
        # Overlapping both phone and email with Alice
        Contact(
            email="alice@example.com",
            phoneNumber="1231231234",
            linkPrecedence="secondary",
            linkedId=1,
        ),
    ]

    db.add_all(contacts)
    db.commit()
    db.close()
    print("✅ Seeded test contacts successfully!")


if __name__ == "__main__":
    seed_contacts()
