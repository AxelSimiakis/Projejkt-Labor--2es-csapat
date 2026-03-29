import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget
)
from PySide6.QtCore import Qt

from views.home_view import HomeView
from views.login_view import LoginView
from views.trailer_list_view import TrailerListView
from views.register_view import RegisterView
from views.profile_view import ProfileView
from views.user_view import UserView
from views.booking_view import BookingView
from views.technical_view import TechnicalView
from views.favorite_view import FavoriteView
from views.cart_view import CartView
from views.my_bookings_view import MyBookingsView
from views.statistics_view import StatisticsView
from core.session_manager import SessionManager
from core.image_utils import create_round_avatar


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PótkocsiPont")
        self.resize(1400, 900)
        self.setMinimumSize(1000, 650)

        main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.navbar = QWidget()
        self.navbar.setObjectName("navbar")
        self.navbar.setFixedHeight(70)

        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(30, 0, 30, 0)
        self.nav_layout.setSpacing(25)
        self.navbar.setLayout(self.nav_layout)

        self.main_layout.addWidget(self.navbar)

        self.stack = QStackedWidget()

        self.home_page = HomeView(self)
        self.login_page = LoginView(self)
        self.trailer_page = TrailerListView(self)
        self.register_page = RegisterView(self)
        self.profile_page = ProfileView(self)
        self.booking_page = BookingView(self)
        self.user_page = UserView(self)
        self.technical_page = TechnicalView(self)
        self.favorite_page = FavoriteView(self)
        self.cart_page = CartView(self)
        self.my_bookings_page = MyBookingsView(self)
        self.statistics_page = StatisticsView(self)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.trailer_page)
        self.stack.addWidget(self.register_page)
        self.stack.addWidget(self.profile_page)
        self.stack.addWidget(self.booking_page)
        self.stack.addWidget(self.user_page)
        self.stack.addWidget(self.technical_page)
        self.stack.addWidget(self.favorite_page)
        self.stack.addWidget(self.cart_page)
        self.stack.addWidget(self.my_bookings_page)
        self.stack.addWidget(self.statistics_page)

        self.main_layout.addWidget(self.stack)

        main_widget.setLayout(self.main_layout)
        self.setCentralWidget(main_widget)

        self.apply_styles()
        self.update_navbar()

    def apply_styles(self):
        self.setStyleSheet("""
        QMainWindow {
            background-color: #646464;
        }

        QWidget {
            background-color: #646464;
        }

        QWidget#navbar {
            background-color: #16a34a;
        }

        QPushButton {
            background: transparent;
            border: none;
            color: white;
            font-size: 18px;
        }

        QPushButton:hover {
            text-decoration: underline;
        }
        """)

    def go_to_home(self):
        self.stack.setCurrentWidget(self.home_page)

    def go_to_trailers(self):
        if hasattr(self.trailer_page, "refresh"):
            self.trailer_page.refresh()
        self.stack.setCurrentWidget(self.trailer_page)

    def open_bookings(self):
        if hasattr(self.booking_page, "load_data"):
            self.booking_page.load_data()
        self.stack.setCurrentWidget(self.booking_page)

    def open_my_bookings(self):
        if hasattr(self.my_bookings_page, "load_data"):
            self.my_bookings_page.load_data()
        self.stack.setCurrentWidget(self.my_bookings_page)

    def open_users(self):
        if hasattr(self.user_page, "load_data"):
            self.user_page.load_data()
        self.stack.setCurrentWidget(self.user_page)

    def open_favorites(self):
        if hasattr(self.favorite_page, "load_data"):
            self.favorite_page.load_data()
        self.stack.setCurrentWidget(self.favorite_page)

    def open_cart(self):
        if hasattr(self.cart_page, "load_data"):
            self.cart_page.load_data()
        self.stack.setCurrentWidget(self.cart_page)

    def open_profile(self):
        if hasattr(self.profile_page, "load_user"):
            self.profile_page.load_user()
        self.stack.setCurrentWidget(self.profile_page)

    def open_technical(self):
        if hasattr(self.technical_page, "load_data"):
            self.technical_page.load_data()
        self.stack.setCurrentWidget(self.technical_page)

    def open_statistics(self):
        if hasattr(self.statistics_page, "refresh_data"):
            self.statistics_page.refresh_data()
        self.stack.setCurrentWidget(self.statistics_page)

    def update_navbar(self):
        while self.nav_layout.count():
            item = self.nav_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        logo_btn = QPushButton("PótkocsiPont")
        logo_btn.setStyleSheet("font-weight: bold; font-size: 20px;")
        logo_btn.clicked.connect(self.go_to_home)

        home_btn = QPushButton("Főoldal")
        trailers_btn = QPushButton("Utánfutó foglalás")

        home_btn.clicked.connect(self.go_to_home)
        trailers_btn.clicked.connect(self.go_to_trailers)

        self.nav_layout.addWidget(logo_btn)
        self.nav_layout.addSpacing(40)
        self.nav_layout.addWidget(home_btn)
        self.nav_layout.addWidget(trailers_btn)
        self.nav_layout.addStretch()

        session = SessionManager.instance()

        if not session.is_authenticated():
            register_btn = QPushButton("Regisztráció")
            register_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.register_page))

            login_btn = QPushButton("Belépés")
            login_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.login_page))

            self.nav_layout.addWidget(register_btn)
            self.nav_layout.addWidget(login_btn)
            return

        user = session.get_user()
        role = user.role if user else None

        avatar_btn = QPushButton()
        avatar_btn.setFixedSize(40, 40)
        avatar_btn.setCursor(Qt.PointingHandCursor)
        avatar_btn.setStyleSheet("""
            border-radius: 20px;
            border: none;
        """)
        avatar_btn.clicked.connect(self.open_profile)

        if user and getattr(user, "profile_image_path", None):
            avatar = create_round_avatar(user.profile_image_path, 40)
            avatar_btn.setIcon(avatar)
            avatar_btn.setIconSize(avatar_btn.size())

        self.nav_layout.addWidget(avatar_btn)

        if role in ["admin", "employee"]:
            bookings_btn = QPushButton("Foglalások")
            bookings_btn.clicked.connect(self.open_bookings)
            self.nav_layout.addWidget(bookings_btn)

        if role == "user":
            my_bookings_btn = QPushButton("Foglalások")
            my_bookings_btn.clicked.connect(self.open_my_bookings)
            self.nav_layout.addWidget(my_bookings_btn)

        if role in ["admin", "employee"]:
            tech_btn = QPushButton("Utánfutók")
            tech_btn.clicked.connect(self.open_technical)
            self.nav_layout.addWidget(tech_btn)

        if role == "admin":
            users_btn = QPushButton("Felhasználók")
            users_btn.clicked.connect(self.open_users)
            self.nav_layout.addWidget(users_btn)

            statistics_btn = QPushButton("Statisztika")
            statistics_btn.clicked.connect(self.open_statistics)
            self.nav_layout.addWidget(statistics_btn)

        favorites_btn = QPushButton("Kedvencek")
        favorites_btn.clicked.connect(self.open_favorites)
        self.nav_layout.addWidget(favorites_btn)

        if role == "user":
            cart_btn = QPushButton("Kosár")
            cart_btn.clicked.connect(self.open_cart)
            self.nav_layout.addWidget(cart_btn)

        profile_btn = QPushButton("Adataim")
        profile_btn.clicked.connect(self.open_profile)
        self.nav_layout.addWidget(profile_btn)

        logout_btn = QPushButton("Kilépés")
        logout_btn.clicked.connect(self.handle_logout)
        self.nav_layout.addWidget(logout_btn)

    def handle_logout(self):
        SessionManager.instance().logout()

        if hasattr(self.trailer_page, "refresh"):
            self.trailer_page.refresh()

        if hasattr(self.favorite_page, "load_data"):
            self.favorite_page.load_data()

        if hasattr(self.cart_page, "load_data"):
            self.cart_page.load_data()

        if hasattr(self.my_bookings_page, "load_data"):
            self.my_bookings_page.load_data()

        if hasattr(self.statistics_page, "refresh_data"):
            self.statistics_page.refresh_data()

        self.update_navbar()
        self.go_to_home()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())