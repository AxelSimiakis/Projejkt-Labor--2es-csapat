from database import SessionLocal
from models import User
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
            role="admin"
        ),
        User(
            email="employee@rental.hu",
            password_hash=hash_password("employee123"),
            first_name="Telepi",
            last_name="Dolgozó",
            role="employee"
        ),
        User(
            email="user1@test.hu",
            password_hash=hash_password("user123"),
            first_name="Teszt",
            last_name="Felhasználó",
            role="user"
        )
    ]

    session.add_all(users)
    session.commit()
    session.close()

if __name__ == "__main__":
    run()