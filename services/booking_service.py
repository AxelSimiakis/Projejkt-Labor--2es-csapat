from database import SessionLocal
from models.booking import Booking

def is_trailer_available(trailer_id, date, period):
    db = SessionLocal()

    bookings = db.query(Booking).filter(
        Booking.trailer_id == trailer_id,
        Booking.date == date
    ).all()

    for b in bookings:

        if b.period == "fullday":
            return False

        if period == "fullday":
            return False

        if b.period == period:
            return False

    return True

def create_booking(user_id, trailer_id, date, period):
    db = SessionLocal()

    booking = Booking(
        user_id=user_id,
        trailer_id=trailer_id,
        date=date,
        period=period
    )

    db.add(booking)
    db.commit()