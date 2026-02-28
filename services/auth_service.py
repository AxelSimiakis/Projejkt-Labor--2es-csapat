import bcrypt
from database import SessionLocal
from models import User


class AuthService:

    @staticmethod
    def login(email: str, password: str):
        session = SessionLocal()

        user = session.query(User).filter_by(email=email).first()

        if not user:
            session.close()
            return False, None

        if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            session.close()
            return True, user

        session.close()
        return False, None