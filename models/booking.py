from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trailer_id = Column(Integer, ForeignKey("trailers.id"), nullable=False)

    booking_date = Column(Date, nullable=False)

    period = Column(String, nullable=False)  
    # morning / afternoon / full_day

    status = Column(String, nullable=False, default="active")
    # active / completed / cancelled / technical

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    trailer = relationship("Trailer")