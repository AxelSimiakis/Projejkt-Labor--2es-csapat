import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Trailer


def create_or_update_trailer(session, **trailer_data):
    existing = session.query(Trailer).filter_by(name=trailer_data["name"]).first()

    if existing:
        existing.description = trailer_data["description"]
        existing.length_cm = trailer_data["length_cm"]
        existing.width_cm = trailer_data["width_cm"]
        existing.max_weight = trailer_data["max_weight"]
        existing.price_morning = trailer_data["price_morning"]
        existing.price_afternoon = trailer_data["price_afternoon"]
        existing.price_full_day = trailer_data["price_full_day"]
        existing.deposit = trailer_data["deposit"]
        existing.late_fee = trailer_data["late_fee"]
        existing.is_active = trailer_data["is_active"]
        existing.image_path = trailer_data["image_path"]

        print(f"Utánfutó frissítve: {trailer_data['name']}")
        return existing

    trailer = Trailer(**trailer_data)
    session.add(trailer)
    print(f"Utánfutó létrehozva: {trailer_data['name']}")
    return trailer


def run():
    session = SessionLocal()

    try:
        create_or_update_trailer(
            session,
            name="WF1",
            description="300x150 cm, 750 kg, általános célú nyitott utánfutó",
            length_cm=300,
            width_cm=150,
            max_weight=450,
            price_morning=5000,
            price_afternoon=5000,
            price_full_day=8500,
            deposit=40000,
            late_fee=5000,
            is_active=True,
            image_path="assets/trailers/wf1.jpg",
        )

        create_or_update_trailer(
            session,
            name="WF3",
            description="205x122 cm, 750 kg, kisebb szállításokhoz ideális",
            length_cm=205,
            width_cm=122,
            max_weight=590,
            price_morning=4000,
            price_afternoon=4000,
            price_full_day=6000,
            deposit=40000,
            late_fee=4000,
            is_active=True,
            image_path="assets/trailers/wf3.jpg",
        )

        create_or_update_trailer(
            session,
            name="AUTO1",
            description="Autószállító utánfutó, rámpával",
            length_cm=450,
            width_cm=210,
            max_weight=2000,
            price_morning=12000,
            price_afternoon=12000,
            price_full_day=20000,
            deposit=80000,
            late_fee=12000,
            is_active=True,
            image_path="assets/trailers/auto1.jpg",
        )

        create_or_update_trailer(
            session,
            name="MAGAS1",
            description="Magasított oldalfalú utánfutó költözéshez",
            length_cm=320,
            width_cm=160,
            max_weight=900,
            price_morning=6500,
            price_afternoon=6500,
            price_full_day=11000,
            deposit=50000,
            late_fee=6500,
            is_active=True,
            image_path="assets/trailers/magas1.jpg",
        )

        session.commit()
        print("A seed_trailers sikeresen lefutott.")
    except Exception as e:
        session.rollback()
        print(f"Hiba történt a trailer seed során: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run()