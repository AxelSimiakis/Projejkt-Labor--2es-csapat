# TrailerRentalApp

Asztali alkalmazás Python + PySide6 + SQLAlchemy használatával egy utánfutó kölcsönző cég számára.

## Projekt célja

Az alkalmazás célja egy utánfutó kölcsönző rendszer megvalósítása, amely:

- vendégként lehetővé teszi az utánfutók megtekintését
- regisztrált felhasználók számára foglalást biztosít
- alkalmazotti és adminisztrátori jogosultságokat kezel
- grafikonos kimutatást tesz lehetővé

---

## Technológiai stack

- Python 3.13
- PySide6 (asztali GUI)
- SQLAlchemy ORM
- Alembic (adatbázis migráció)
- SQLite
- bcrypt (jelszó hash)

---

## Architektúra

MVVM alapú felépítés:

- models → ORM adatmodellek
- services → üzleti logika
- viewmodels → ViewModel réteg
- views → PySide6 GUI
- migrations → Alembic migrációk
- seed → minta adatok

---

## Adatbázis POC

Megvalósított elemek:

- ORM alapú modellek
- Identity rendszer (bcrypt)
- Role alapú jogosultság (admin, employee, user)
- Kapcsolatok (Foreign Key)
- Alembic migráció rendszer
- Seed minta adatok

---

## Futatási útmutató

### 1. Virtuális környezet aktiválása

venv\Scripts\activate


### 2. Csomagok telepítése

pip install -r requirements.txt


### Migráció futtatása

alembic upgrade head


### Minta adatok betöltése

python seed/seed_users.py
python seed/seed_trailers.py
python seed/seed_bookings.py


### Alkalmazások indítása

python app.py