import os
import sys
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Booking, User, Trailer


def booking_exists(session, user_id, trailer_id, booking_date, period, status):
    return session.query(Booking).filter_by(
        user_id=user_id,
        trailer_id=trailer_id,
        booking_date=booking_date,
        period=period,
        status=status
    ).first() is not None


def create_booking_if_not_exists(session, user_id, trailer_id, booking_date, period, status):
    if booking_exists(session, user_id, trailer_id, booking_date, period, status):
        print(
            f"Ez a foglalás már létezik: "
            f"user_id={user_id}, trailer_id={trailer_id}, date={booking_date}, period={period}, status={status}"
        )
        return

    booking = Booking(
        user_id=user_id,
        trailer_id=trailer_id,
        booking_date=booking_date,
        period=period,
        status=status,
    )
    session.add(booking)
    print(
        f"Foglalás létrehozva: "
        f"user_id={user_id}, trailer_id={trailer_id}, date={booking_date}, period={period}, status={status}"
    )


def run():
    session = SessionLocal()

    try:
        user = session.query(User).filter_by(email="user1@test.hu").first()
        employee = session.query(User).filter_by(email="employee@rental.hu").first()

        trailer_wf1 = session.query(Trailer).filter_by(name="Nyitott utánfutó").first()
        trailer_wf2 = session.query(Trailer).filter_by(name="Kerékpár szállító").first()
        trailer_wf3 = session.query(Trailer).filter_by(name="Egytengelyes").first()

        if not user:
            print("Hiányzik a user1@test.hu felhasználó. Futtasd előbb: python seed/seed_users.py")
            return

        if not employee:
            print("Hiányzik az employee@rental.hu felhasználó. Futtasd előbb: python seed/seed_users.py")
            return

        if not trailer_wf1 or not trailer_wf2 or not trailer_wf3:
            print("Hiányzó trailer adatok. Futtasd előbb: python seed/seed_trailers.py")
            return

        create_booking_if_not_exists(
            session,
            user_id=user.id,
            trailer_id=trailer_wf1.id,
            booking_date=date.today(),
            period="morning",
            status="active",
        )

        create_booking_if_not_exists(
            session,
            user_id=user.id,
            trailer_id=trailer_wf2.id,
            booking_date=date.today() + timedelta(days=1),
            period="afternoon",
            status="active",
        )

        create_booking_if_not_exists(
            session,
            user_id=employee.id,
            trailer_id=trailer_wf3.id,
            booking_date=date.today() + timedelta(days=2),
            period="full_day",
            status="technical",
        )

        session.commit()
        print("A seed_bookings sikeresen lefutott.")
    except Exception as e:
        session.rollback()
        print(f"Hiba történt a booking seed során: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run()