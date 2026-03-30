from datetime import date

from database import SessionLocal
from models import Trailer
from models.booking import Booking
from services.email_service import send_system_cancellation_email


class TrailerService:

    @staticmethod
    def get_all_trailers(only_active: bool = True):
        session = SessionLocal()
        try:
            query = session.query(Trailer)
            if only_active:
                query = query.filter_by(is_active=True)
            return query.order_by(Trailer.name.asc()).all()
        finally:
            session.close()

    @staticmethod
    def get_trailer_by_id(trailer_id: int):
        session = SessionLocal()
        try:
            return session.query(Trailer).filter_by(id=trailer_id, is_active=True).first()
        finally:
            session.close()

    @staticmethod
    def set_trailer_service_until(trailer_id: int, service_until):
        session = SessionLocal()

        try:
            trailer = session.query(Trailer).filter(Trailer.id == trailer_id).first()
            if not trailer:
                raise ValueError("Az utánfutó nem található.")

            today = date.today()

            if service_until < today:
                raise ValueError("A szerviz dátuma nem lehet múltbeli.")

            trailer.status = "service"

            affected_bookings = (
                session.query(Booking)
                .filter(
                    Booking.trailer_id == trailer.id,
                    Booking.status == "active",
                    Booking.booking_date >= today,
                    Booking.booking_date <= service_until,
                )
                .all()
            )

            cancelled_bookings_for_email = []

            for booking in affected_bookings:
                booking.status = "cancelled"

                if booking.user and booking.user.email:
                    full_name = f"{booking.user.first_name or ''} {booking.user.last_name or ''}".strip()
                    cancelled_bookings_for_email.append({
                        "email": booking.user.email,
                        "name": full_name if full_name else "Felhasználó",
                        "trailer_name": trailer.name,
                        "booking_date": booking.booking_date,
                        "period": booking.period,
                    })

            session.commit()

            for item in cancelled_bookings_for_email:
                try:
                    send_system_cancellation_email(
                        recipient_email=item["email"],
                        recipient_name=item["name"],
                        trailer_name=item["trailer_name"],
                        booking_date=item["booking_date"],
                        period=item["period"],
                        reason=f"Az utánfutó szervizbe került, ezért a foglalás a {service_until.strftime('%Y.%m.%d.')} dátumig terjedő időszakban nem teljesíthető."
                    )
                except Exception as e:
                    print("EMAIL HIBA (szerviz):", e)

            return {
                "cancelled_count": len(cancelled_bookings_for_email),
                "cancelled_bookings": cancelled_bookings_for_email,
            }

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def set_trailer_inactive(trailer_id: int):
        session = SessionLocal()

        try:
            trailer = session.query(Trailer).filter(Trailer.id == trailer_id).first()
            if not trailer:
                raise ValueError("Az utánfutó nem található.")

            today = date.today()

            trailer.status = "inactive"

            affected_bookings = (
                session.query(Booking)
                .filter(
                    Booking.trailer_id == trailer.id,
                    Booking.status == "active",
                    Booking.booking_date >= today,
                )
                .all()
            )

            cancelled_bookings_for_email = []

            for booking in affected_bookings:
                booking.status = "cancelled"

                if booking.user and booking.user.email:
                    full_name = f"{booking.user.first_name or ''} {booking.user.last_name or ''}".strip()
                    cancelled_bookings_for_email.append({
                        "email": booking.user.email,
                        "name": full_name if full_name else "Felhasználó",
                        "trailer_name": trailer.name,
                        "booking_date": booking.booking_date,
                        "period": booking.period,
                    })

            session.commit()

            for item in cancelled_bookings_for_email:
                try:
                    send_system_cancellation_email(
                        recipient_email=item["email"],
                        recipient_name=item["name"],
                        trailer_name=item["trailer_name"],
                        booking_date=item["booking_date"],
                        period=item["period"],
                        reason="Az utánfutó inaktív állapotba került, ezért a jövőbeli foglalás nem teljesíthető."
                    )
                except Exception as e:
                    print("EMAIL HIBA (inactive):", e)

            return {
                "cancelled_count": len(cancelled_bookings_for_email),
                "cancelled_bookings": cancelled_bookings_for_email,
            }

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def set_trailer_available(trailer_id: int):
        session = SessionLocal()

        try:
            trailer = session.query(Trailer).filter(Trailer.id == trailer_id).first()
            if not trailer:
                raise ValueError("Az utánfutó nem található.")

            trailer.status = "available"
            session.commit()

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()