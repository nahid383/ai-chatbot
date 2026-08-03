"""
One-time script to create the first admin account (you, the CR),
since students can't self-register and there's no admin yet on a
fresh database.

Run with:  python -m app.seed
"""

from app.database import SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)


def seed_admin():
    db = SessionLocal()
    try:
        email = input("Admin email: ").strip()
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("A user with this email already exists. Aborting.")
            return

        full_name = input("Admin full name: ").strip()
        password = input("Admin password (temporary, change it later): ").strip()

        admin = User(
            full_name=full_name,
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.admin,
        )
        db.add(admin)
        db.commit()
        print(f"Admin account created for {email}.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
