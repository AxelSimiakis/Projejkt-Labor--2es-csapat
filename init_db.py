from database import engine
from models.base import Base
from models.user import User
from models.trailer import Trailer
from models.booking import Booking
from models.favorite import Favorite
from models.cart_item import CartItem

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Táblák létrehozva.")