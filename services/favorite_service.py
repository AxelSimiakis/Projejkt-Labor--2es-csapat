from database import SessionLocal
from models.favorite import Favorite
from models.trailer import Trailer


def get_favorite_trailer_ids(user_id: int) -> set[int]:
    session = SessionLocal()
    try:
        favorites = session.query(Favorite).filter_by(user_id=user_id).all()
        return {fav.trailer_id for fav in favorites}
    finally:
        session.close()


def is_favorite(user_id: int, trailer_id: int) -> bool:
    session = SessionLocal()
    try:
        favorite = session.query(Favorite).filter_by(
            user_id=user_id,
            trailer_id=trailer_id
        ).first()
        return favorite is not None
    finally:
        session.close()


def add_favorite(user_id: int, trailer_id: int) -> bool:
    session = SessionLocal()
    try:
        existing = session.query(Favorite).filter_by(
            user_id=user_id,
            trailer_id=trailer_id
        ).first()

        if existing:
            return False

        session.add(Favorite(user_id=user_id, trailer_id=trailer_id))
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def remove_favorite(user_id: int, trailer_id: int) -> bool:
    session = SessionLocal()
    try:
        favorite = session.query(Favorite).filter_by(
            user_id=user_id,
            trailer_id=trailer_id
        ).first()

        if not favorite:
            return False

        session.delete(favorite)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def toggle_favorite(user_id: int, trailer_id: int) -> bool:
    """
    Visszatérés:
    True  -> most kedvenc lett
    False -> most eltávolítottuk a kedvencekből
    """
    session = SessionLocal()
    try:
        favorite = session.query(Favorite).filter_by(
            user_id=user_id,
            trailer_id=trailer_id
        ).first()

        if favorite:
            session.delete(favorite)
            session.commit()
            return False

        session.add(Favorite(user_id=user_id, trailer_id=trailer_id))
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_user_favorite_trailers(user_id: int):
    session = SessionLocal()
    try:
        trailers = (
            session.query(Trailer)
            .join(Favorite, Favorite.trailer_id == Trailer.id)
            .filter(Favorite.user_id == user_id)
            .order_by(Trailer.name.asc())
            .all()
        )
        return trailers
    finally:
        session.close()