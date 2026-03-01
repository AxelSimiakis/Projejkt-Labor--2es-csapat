from database import SessionLocal
from models.trailer import Trailer


class TrailerListViewModel:

    def get_all_trailers(self):
        session = SessionLocal()
        trailers = session.query(Trailer).all()
        session.close()
        return trailers