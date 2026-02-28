from database import SessionLocal
from models.user import User
from passlib.hash import bcrypt


class LoginViewModel:

    def login(self, email, password):

        session = SessionLocal()
        user = session.query(User).filter_by(email=email).first()

        if user and bcrypt.verify(password, user.password_hash):
            session.close()
            return True, user

        session.close()
        return False, None