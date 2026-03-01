from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)

    # ===== ÚJ CÍM MEZŐK =====
    country = Column(String)
    zip_code = Column(String)
    city = Column(String)
    street = Column(String)
    house_number = Column(String)

    profile_image_path = Column(String)

    role = Column(String, default="user")

    created_at = Column(DateTime(timezone=True), server_default=func.now())