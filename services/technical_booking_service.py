from database import SessionLocal
from models.user import User
from models.booking import Booking
from services.booking_service import is_trailer_available
from services.email_service import send_booking_confirmation_email
from services.email_service import send_registration_email
from passlib.hash import bcrypt


def create_technical_booking(
    first_name, last_name, phone, email, password,
    country, zip_code, city, street, house_number,
    trailer_id, booking_date, period
):
    session = SessionLocal()
    try:
        new_user_created = False

        if not all([first_name, last_name, email, phone]):
            raise ValueError("Minden kötelező mezőt tölts ki!")

        user = session.query(User).filter_by(email=email).first()

        if not user:
            new_user_created = True

            user = User(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                password_hash=bcrypt.hash(password),
                country=country,
                zip_code=zip_code,
                city=city,
                street=street,
                house_number=house_number,
                role="user"
            )
            session.add(user)
            session.flush()

        if not is_trailer_available(trailer_id, booking_date, period):
            raise ValueError("Az utánfutó nem elérhető!")

        booking = Booking(
            user_id=user.id,
            trailer_id=trailer_id,
            booking_date=booking_date,
            period=period,
            status="technical",
            name="Technikai foglalás",
            phone=phone,
        )

        session.add(booking)
        session.commit()

        if new_user_created:
            send_registration_email(
                email=email,
                name=f"{first_name} {last_name}",
                password=password if password else "123456"
            )

        trailer_name = booking.trailer.name if booking.trailer else "Utánfutó"
        trailer = booking.trailer

        price = 0
        if trailer:
            if period == "morning":
                price = trailer.price_morning or 0
            elif period == "afternoon":
                price = trailer.price_afternoon or 0
            elif period == "full_day":
                price = trailer.price_full_day or 0

        deposit = trailer.deposit or 0 if trailer else 0

        send_booking_confirmation_email(
            recipient_email=email,
            recipient_name=f"{first_name} {last_name}",
            bookings=[{
                "trailer_name": trailer.name,
                "booking_date": booking_date,
                "period": period,
                "price": price,
                "deposit": deposit
            }]
        )

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()