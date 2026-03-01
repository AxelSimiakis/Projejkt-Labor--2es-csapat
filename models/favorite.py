from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trailer_id = Column(Integer, ForeignKey("trailers.id"), nullable=False)

    user = relationship("User")
    trailer = relationship("Trailer")

    __table_args__ = (
        UniqueConstraint("user_id", "trailer_id", name="unique_user_trailer"),
    )