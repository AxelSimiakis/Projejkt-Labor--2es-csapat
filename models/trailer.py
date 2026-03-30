from sqlalchemy import Column, Integer, String, Boolean
from models.base import Base


class Trailer(Base):
    __tablename__ = "trailers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    length_cm = Column(Integer, nullable=True)
    width_cm = Column(Integer, nullable=True)
    max_weight = Column(Integer, nullable=True)

    price_morning = Column(Integer, nullable=False, default=0)
    price_afternoon = Column(Integer, nullable=False, default=0)
    price_full_day = Column(Integer, nullable=False, default=0)

    deposit = Column(Integer, nullable=False, default=0)
    late_fee = Column(Integer, nullable=False, default=0)

    is_active = Column(Boolean, default=True)
    image_path = Column(String, nullable=True)

    # available | service | inactive
    status = Column(String, nullable=False, default="available")