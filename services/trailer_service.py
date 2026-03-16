from database import SessionLocal
from models import Trailer


class TrailerService:

    @staticmethod
    def get_all_trailers(only_active: bool = True):
        session = SessionLocal()
        try:
            query = session.query(Trailer)
            if only_active:
                query = query.filter_by(is_active=True)
            return query.order_by(Trailer.name.asc()).all()
        finally:
            session.close()

    @staticmethod
    def get_trailer_by_id(trailer_id: int):
        session = SessionLocal()
        try:
            return session.query(Trailer).filter_by(id=trailer_id, is_active=True).first()
        finally:
            session.close()