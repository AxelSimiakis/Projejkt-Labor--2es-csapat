from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship

from models.base import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trailer_id = Column(Integer, ForeignKey("trailers.id"), nullable=False)

    booking_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    period = Column(Integer, nullable=False)
    # 0 = morning
    # 1 = afternoon
    # 2 = full_day

    user = relationship("User")
    trailer = relationship("Trailer")