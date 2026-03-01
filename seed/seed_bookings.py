import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Booking, User, Trailer
from datetime import date

def run():
    session = SessionLocal()

    user = session.query(User).filter_by(email="user1@test.hu").first()
    trailer = session.query(Trailer).filter_by(name="WF1").first()

    booking = Booking(
        user_id=user.id,
        trailer_id=trailer.id,
        booking_date=date.today(),
        period="full_day",
        status="active"
    )

    session.add(booking)
    session.commit()
    session.close()

if __name__ == "__main__":
    run()