import os
import sys
from datetime import datetime, UTC

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_user_if_not_exists(session, **user_data):
    existing_user = session.query(User).filter_by(email=user_data["email"]).first()
    if existing_user:
        print(f"Ez a felhasználó már létezik: {user_data['email']}")
        return existing_user

    user = User(**user_data)
    session.add(user)
    print(f"Felhasználó létrehozva: {user_data['email']}")
    return user


def run():
    session = SessionLocal()

    try:
        create_user_if_not_exists(
            session,
            email="admin@admin.hu",
            password_hash=hash_password("admin123"),
            first_name="Admin",
            last_name="User",
            phone="06201234567",
            country="Magyarország",
            zip_code="1111",
            city="Budapest",
            street="Fő utca",
            house_number="1",
            profile_image_path=None,
            role="admin",
            created_at=datetime.now(UTC),
        )

        create_user_if_not_exists(
            session,
            email="employee@rental.hu",
            password_hash=hash_password("employee123"),
            first_name="Telepi",
            last_name="Dolgozó",
            phone="06301234567",
            country="Magyarország",
            zip_code="2222",
            city="Győr",
            street="Raktár utca",
            house_number="12",
            profile_image_path=None,
            role="employee",
            created_at=datetime.now(UTC),
        )

        create_user_if_not_exists(
            session,
            email="user1@test.hu",
            password_hash=hash_password("user123"),
            first_name="Teszt",
            last_name="Felhasználó",
            phone="06701234567",
            country="Magyarország",
            zip_code="3333",
            city="Szeged",
            street="Minta utca",
            house_number="5",
            profile_image_path=None,
            role="user",
            created_at=datetime.now(UTC),
        )

        session.commit()
        print("A seed_users sikeresen lefutott.")
    except Exception as e:
        session.rollback()
        print(f"Hiba történt seed közben: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run()