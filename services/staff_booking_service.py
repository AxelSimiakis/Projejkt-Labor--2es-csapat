from passlib.hash import bcrypt

from database import SessionLocal
from models.user import User
from services.booking_service import create_booking
from services.email_service import send_booking_confirmation_email, send_registration_email


def create_staff_booking(
    first_name, last_name, phone, email, password,
    country, zip_code, city, street, house_number,
    trailer_id, booking_date, period,
):
    session = SessionLocal()
    try:
        if not all([first_name, last_name, email, phone]):
            raise ValueError("Minden kötelező mezőt tölts ki!")

        new_user_created = False
        user = session.query(User).filter_by(email=email).first()

        if not user:
            new_user_created = True
            resolved_password = password or "123456"

            user = User(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                password_hash=bcrypt.hash(resolved_password),
                country=country,
                zip_code=zip_code,
                city=city,
                street=street,
                house_number=house_number,
                role="user",
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        else:
            if phone:
                user.phone = phone
            if country:
                user.country = country
            if zip_code:
                user.zip_code = zip_code
            if city:
                user.city = city
            if street:
                user.street = street
            if house_number:
                user.house_number = house_number
            session.commit()

        booking = create_booking(
            user_id=user.id,
            trailer_id=trailer_id,
            booking_date=booking_date,
            period=period,
            status="employee",
        )

        if new_user_created:
            send_registration_email(
                email=email,
                name=f"{first_name} {last_name}",
                password=password or "123456",
            )

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
                "trailer_name": trailer.name if trailer else "Utánfutó",
                "booking_date": booking_date,
                "period": period,
                "price": price,
                "deposit": deposit,
            }]
        )

        return booking

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
