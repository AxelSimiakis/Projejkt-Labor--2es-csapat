from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)

    amount = Column(Integer, nullable=False)

    method = Column(String, nullable=False)
    # cash / card

    status = Column(String, nullable=False, default="pending")
    # pending / paid / failed

    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking")