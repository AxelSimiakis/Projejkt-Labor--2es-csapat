from sqlalchemy import Column, Integer, String, Boolean
from .base import Base

class Trailer(Base):
    __tablename__ = "trailers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    description = Column(String)

    length_cm = Column(Integer)
    width_cm = Column(Integer)
    max_weight = Column(Integer)

    price_morning = Column(Integer, nullable=False)
    price_afternoon = Column(Integer, nullable=False)
    price_full_day = Column(Integer, nullable=False)

    deposit = Column(Integer, nullable=False)
    late_fee = Column(Integer, nullable=False)

    is_active = Column(Boolean, default=True)