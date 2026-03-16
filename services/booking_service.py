from datetime import date

from database import SessionLocal
from models.booking import Booking

FULL_DAY = "full_day"
MORNING = "morning"
AFTERNOON = "afternoon"
ACTIVE_STATUSES = ["active", "technical"]


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


def get_availability_for_trailer_and_date(trailer_id: int, booking_date: date) -> dict:
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


def is_trailer_available(trailer_id: int, booking_date: date, period: str) -> bool:
    normalized_period = _normalize_period(period)
    availability = get_availability_for_trailer_and_date(trailer_id, booking_date)
    return availability[normalized_period]


def create_booking(user_id: int, trailer_id: int, booking_date: date, period: str, status: str = "active"):
    normalized_period = _normalize_period(period)

    session = SessionLocal()
    try:
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