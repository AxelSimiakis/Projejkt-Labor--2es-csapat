from datetime import date, timedelta

from database import SessionLocal
from models.booking import Booking
from models.trailer import Trailer

FULL_DAY = "full_day"
MORNING = "morning"
AFTERNOON = "afternoon"
ACTIVE_STATUSES = ["active", "employee", "technical"]


def _normalize_period(period: str) -> str:
    if not period:
        raise ValueError("Az időszak megadása kötelező.")

    normalized = period.strip().lower()

    if normalized == "fullday":
        normalized = FULL_DAY

    if normalized not in {MORNING, AFTERNOON, FULL_DAY}:
        raise ValueError("Érvénytelen időszak.")

    return normalized


def get_bookings_for_trailer_and_date(trailer_id: int, booking_date: date):
    session = SessionLocal()
    try:
        return (
            session.query(Booking)
            .filter(
                Booking.trailer_id == trailer_id,
                Booking.booking_date == booking_date,
                Booking.status.in_(ACTIVE_STATUSES),
            )
            .all()
        )
    finally:
        session.close()


def get_bookings_for_trailer_between_dates(trailer_id: int, start_date: date, end_date: date):
    session = SessionLocal()
    try:
        return (
            session.query(Booking)
            .filter(
                Booking.trailer_id == trailer_id,
                Booking.booking_date >= start_date,
                Booking.booking_date <= end_date,
                Booking.status.in_(ACTIVE_STATUSES),
            )
            .all()
        )
    finally:
        session.close()


def get_trailer_status(trailer_id: int):
    session = SessionLocal()
    try:
        trailer = session.query(Trailer).filter(Trailer.id == trailer_id).first()
        if not trailer:
            return None
        return trailer.status
    finally:
        session.close()


def is_trailer_bookable(trailer_id: int) -> bool:
    session = SessionLocal()
    try:
        trailer = session.query(Trailer).filter(Trailer.id == trailer_id).first()
        if not trailer:
            return False

        if not trailer.is_active:
            return False

        if trailer.status in ["service", "inactive"]:
            return False

        return True
    finally:
        session.close()


def get_availability_for_trailer_and_date(trailer_id: int, booking_date: date) -> dict:
    if not is_trailer_bookable(trailer_id):
        return {
            MORNING: False,
            AFTERNOON: False,
            FULL_DAY: False,
        }

    bookings = get_bookings_for_trailer_and_date(trailer_id, booking_date)

    availability = {
        MORNING: True,
        AFTERNOON: True,
        FULL_DAY: True,
    }

    for booking in bookings:
        period = _normalize_period(booking.period)

        if period == FULL_DAY:
            availability[MORNING] = False
            availability[AFTERNOON] = False
            availability[FULL_DAY] = False
            return availability

        if period == MORNING:
            availability[MORNING] = False
            availability[FULL_DAY] = False

        if period == AFTERNOON:
            availability[AFTERNOON] = False
            availability[FULL_DAY] = False

    return availability


def get_availability_map_for_period(trailer_id: int, start_date: date, end_date: date) -> dict:
    if not is_trailer_bookable(trailer_id):
        result = {}
        current = start_date
        while current <= end_date:
            result[current] = "full"
            current += timedelta(days=1)
        return result

    bookings = get_bookings_for_trailer_between_dates(trailer_id, start_date, end_date)

    grouped = {}
    for booking in bookings:
        grouped.setdefault(booking.booking_date, []).append(_normalize_period(booking.period))

    result = {}
    current = start_date
    while current <= end_date:
        periods = grouped.get(current, [])

        if FULL_DAY in periods:
            result[current] = "full"
        elif MORNING in periods or AFTERNOON in periods:
            if MORNING in periods and AFTERNOON in periods:
                result[current] = "full"
            else:
                result[current] = "partial"
        else:
            result[current] = "free"

        current += timedelta(days=1)

    return result


def is_trailer_available(trailer_id: int, booking_date: date, period: str) -> bool:
    normalized_period = _normalize_period(period)
    availability = get_availability_for_trailer_and_date(trailer_id, booking_date)
    return availability[normalized_period]


def create_booking(user_id: int, trailer_id: int, booking_date: date, period: str, status: str = "active"):
    normalized_period = _normalize_period(period)

    session = SessionLocal()
    try:
        trailer = session.query(Trailer).filter(Trailer.id == trailer_id).first()

        if not trailer:
            raise ValueError("Az utánfutó nem található.")

        if not trailer.is_active:
            raise ValueError("Az utánfutó inaktív.")

        if trailer.status == "service":
            raise ValueError("Az utánfutó jelenleg szerviz alatt van, ezért nem foglalható.")

        if trailer.status == "inactive":
            raise ValueError("Az utánfutó jelenleg üzemen kívüli, ezért nem foglalható.")

        if status == "active" and not is_trailer_available(trailer_id, booking_date, normalized_period):
            raise ValueError("Az utánfutó a kiválasztott időpontra már nem elérhető.")

        booking = Booking(
            user_id=user_id,
            trailer_id=trailer_id,
            booking_date=booking_date,
            period=normalized_period,
            status=status,
        )

        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def cancel_booking(booking_id: int, user_id: int = None, is_admin: bool = False):
    session = SessionLocal()
    try:
        booking = session.query(Booking).filter(Booking.id == booking_id).first()

        if not booking:
            raise ValueError("A foglalás nem található.")

        if booking.status == "cancelled":
            raise ValueError("A foglalás már törölve van.")

        if not is_admin:
            if user_id is None or booking.user_id != user_id:
                raise ValueError("Nincs jogosultságod a foglalás törléséhez.")

            today = date.today()
            days_left = (booking.booking_date - today).days

            if days_left < 5:
                raise ValueError("Az utolsó 5 napban a foglalás már nem törölhető.")

        booking.status = "cancelled"
        session.commit()
        session.refresh(booking)
        return booking

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()