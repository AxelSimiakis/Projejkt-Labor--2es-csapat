from datetime import date, timedelta

from database import SessionLocal
from models.booking import Booking
from models.user import User
from services.email_service import send_booking_cancellation_email


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


def get_availability_map_for_period(trailer_id: int, start_date: date, end_date: date) -> dict:
    """
    Visszatérés:
    {
        date(2026, 3, 18): "free" | "partial" | "full"
    }
    """
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
            # ha legalább egyik félnap foglalt
            if MORNING in periods and AFTERNOON in periods:
                result[current] = "full"
            else:
                result[current] = "partial"
        else:
            result[current] = "free"

        from datetime import timedelta
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

def cancel_booking(booking_id: int, user_id: int):
    session = SessionLocal()
    try:
        booking = session.query(Booking).filter_by(id=booking_id, user_id=user_id).first()

        if not booking:
            raise ValueError("Foglalás nem található.")

        today = date.today()

        # ❌ ha 5 napon belül van
        if booking.booking_date <= today + timedelta(days=5):
            raise ValueError("A foglalás már nem mondható le (5 napon belül).")

        # adatok emailhez
        trailer_name = booking.trailer.name if booking.trailer else f"#{booking.trailer_id}"

        session.delete(booking)
        session.commit()

        # email
        user = session.query(User).filter_by(id=user_id).first()
        if user and user.email:
            send_booking_cancellation_email(
                recipient_email=user.email,
                recipient_name=user.first_name or user.email,
                trailer_name=trailer_name,
                booking_date=booking.booking_date,
                period=booking.period
            )

        return True

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()