from database import SessionLocal
from models import Trailer


class TrailerService:

    @staticmethod
    def get_all_trailers():
        session = SessionLocal()
        trailers = session.query(Trailer).filter_by(is_active=True).all()
        session.close()
        return trailers