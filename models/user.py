from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    phone = Column(String)
    address = Column(String)
    profile_image_path = Column(String)

    role = Column(String, nullable=False, default="user")

    created_at = Column(DateTime, default=datetime.utcnow)