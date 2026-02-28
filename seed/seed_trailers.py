from database import SessionLocal
from models import Trailer

def run():
    session = SessionLocal()

    trailers = [
        Trailer(
            name="WF1",
            description="300x150 cm, 750 kg",
            length_cm=300,
            width_cm=150,
            max_weight=450,
            price_morning=5000,
            price_afternoon=5000,
            price_full_day=8500,
            deposit=40000,
            late_fee=5000
        ),
        Trailer(
            name="WF3",
            description="205x122 cm, 750 kg",
            length_cm=205,
            width_cm=122,
            max_weight=590,
            price_morning=4000,
            price_afternoon=4000,
            price_full_day=6000,
            deposit=40000,
            late_fee=4000
        )
    ]

    session.add_all(trailers)
    session.commit()
    session.close()

if __name__ == "__main__":
    run()