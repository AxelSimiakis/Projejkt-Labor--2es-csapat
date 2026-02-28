import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adatbázis fájl elérési út stabilizálása
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'trailer_rental.db')}"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)