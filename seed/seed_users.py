from database import SessionLocal
from models.user import User
from datetime import datetime
import bcrypt


def hash_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def run():
    session = SessionLocal()

    users = [
        User(
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
            role="admin",
            created_at=datetime.utcnow()
        ),
        User(
            email="employee@rental.hu",
            password_hash=hash_password("employee123"),
            first_name="Telepi",
            last_name="Dolgozó",
            phone="06301234567",
            country="Magyarország",
            zip_code="2222",
            city="Debrecen",
            street="Kossuth utca",
            house_number="10",
            role="employee",
            created_at=datetime.utcnow()
        ),
        User(
            email="user1@test.hu",
            password_hash=hash_password("user123"),
            first_name="Teszt",
            last_name="Felhasználó",
            phone="06701234567",
            country="Magyarország",
            zip_code="3333",
            city="Szeged",
            street="Petőfi utca",
            house_number="5",
            role="user",
            created_at=datetime.utcnow()
        )
    ]

    session.add_all(users)
    session.commit()
    session.close()

    print("Seed users sikeresen létrehozva!")


if __name__ == "__main__":
    run()