from database import SessionLocal
from models.cart_item import CartItem
from models.booking import Booking
from models.user import User
from services.booking_service import is_trailer_available
from services.email_service import send_booking_confirmation_email


PERIOD_TO_INT = {
    "morning": 0,
    "afternoon": 1,
    "full_day": 2,
}

INT_TO_PERIOD = {
    0: "morning",
    1: "afternoon",
    2: "full_day",
}

PERIOD_TO_HU = {
    "morning": "Délelőtt",
    "afternoon": "Délután",
    "full_day": "Egész nap",
}


def period_str_to_int(period: str) -> int:
    return PERIOD_TO_INT[period]


def period_int_to_str(period_value: int) -> str:
    return INT_TO_PERIOD[period_value]


def period_int_to_hu(period_value: int) -> str:
    return PERIOD_TO_HU[INT_TO_PERIOD[period_value]]


def add_to_cart(user_id: int, trailer_id: int, booking_date, period: str):
    session = SessionLocal()
    try:
        period_value = period_str_to_int(period)

        existing = session.query(CartItem).filter_by(
            user_id=user_id,
            trailer_id=trailer_id,
            booking_date=booking_date,
            period=period_value
        ).first()

        if existing:
            raise ValueError("Ez a tétel már szerepel a kosárban.")

        item = CartItem(
            user_id=user_id,
            trailer_id=trailer_id,
            booking_date=booking_date,
            period=period_value,
        )

        session.add(item)
        session.commit()
        session.refresh(item)
        return item
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_user_cart_items(user_id: int):
    session = SessionLocal()
    try:
        items = (
            session.query(CartItem)
            .filter(CartItem.user_id == user_id)
            .order_by(CartItem.created_at.asc())
            .all()
        )

        result = []
        for item in items:
            result.append({
                "id": item.id,
                "trailer_id": item.trailer_id,
                "trailer_name": item.trailer.name if item.trailer else f"#{item.trailer_id}",
                "booking_date": item.booking_date,
                "period": period_int_to_str(item.period),
                "period_hu": period_int_to_hu(item.period),
                "deposit": item.trailer.deposit,
                "price": (
                    item.trailer.price_morning if item.period == 0 else
                    item.trailer.price_afternoon if item.period == 1 else
                    item.trailer.price_full_day
                ) if item.trailer else 0,
            })
        return result
    finally:
        session.close()


def remove_cart_item(cart_item_id: int, user_id: int):
    session = SessionLocal()
    try:
        item = session.query(CartItem).filter_by(id=cart_item_id, user_id=user_id).first()
        if not item:
            return False

        session.delete(item)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def clear_cart(user_id: int):
    session = SessionLocal()
    try:
        items = session.query(CartItem).filter_by(user_id=user_id).all()
        for item in items:
            session.delete(item)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def checkout_cart(user_id: int):
    session = SessionLocal()
    try:
        items = (
            session.query(CartItem)
            .filter_by(user_id=user_id)
            .order_by(CartItem.created_at.asc())
            .all()
        )

        if not items:
            raise ValueError("A kosár üres.")

        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise ValueError("A felhasználó nem található.")

        # 1. Elérhetőség ellenőrzése
        for item in items:
            period = period_int_to_str(item.period)
            available = is_trailer_available(item.trailer_id, item.booking_date, period)

            if not available:
                trailer_name = item.trailer.name if item.trailer else f"#{item.trailer_id}"
                raise ValueError(
                    f"A következő tétel már nem elérhető: "
                    f"{trailer_name} - {item.booking_date} - {period_int_to_hu(item.period)}"
                )

        # 2. Emailhez adatok összegyűjtése még commit előtt
        email_items = []
        for item in items:
            trailer_name = item.trailer.name if item.trailer else f"#{item.trailer_id}"

            price = 0
            if item.trailer:
                if item.period == 0:
                    price = item.trailer.price_morning or 0
                elif item.period == 1:
                    price = item.trailer.price_afternoon or 0
                elif item.period == 2:
                    price = item.trailer.price_full_day or 0

            email_items.append({
                "trailer_name": trailer_name,
                "booking_date": item.booking_date,
                "period": period_int_to_str(item.period),
                "deposit": item.trailer.deposit if item.trailer else 0,
                "price": price,
            })

        # 3. Foglalások létrehozása
        for item in items:
            booking = Booking(
                user_id=item.user_id,
                trailer_id=item.trailer_id,
                booking_date=item.booking_date,
                period=period_int_to_str(item.period),
                status="active",
            )
            session.add(booking)

        # 4. Kosár ürítése
        for item in items:
            session.delete(item)

        session.commit()

        # 5. E-mail küldés commit után
        try:
            if user.email:
                full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                recipient_name = full_name if full_name else user.email

                send_booking_confirmation_email(
                    recipient_email=user.email,
                    recipient_name=recipient_name,
                    bookings=email_items
                )
        except Exception as email_error:
            print(f"E-mail küldési hiba: {email_error}")

        return True

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()