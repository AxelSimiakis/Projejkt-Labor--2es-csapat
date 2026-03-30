import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QMenu
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

        # ===== NAVBAR =====
        self.navbar = QWidget()
        self.navbar.setObjectName("navbar")
        self.navbar.setFixedHeight(70)

        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(30, 0, 30, 0)
        self.nav_layout.setSpacing(20)
        self.navbar.setLayout(self.nav_layout)

        self.main_layout.addWidget(self.navbar)

        # ===== STACK =====
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

        for page in [
            self.home_page, self.login_page, self.trailer_page,
            self.register_page, self.profile_page, self.booking_page,
            self.user_page, self.technical_page, self.favorite_page,
            self.cart_page, self.my_bookings_page, self.statistics_page
        ]:
            self.stack.addWidget(page)

        self.main_layout.addWidget(self.stack)

        main_widget.setLayout(self.main_layout)
        self.setCentralWidget(main_widget)

        # ===== MENU =====
        self.menu = QMenu(self)
        self.menu.setStyleSheet("""
        QMenu {
            background-color: #1f2937;
            color: white;
            border-radius: 8px;
            padding: 5px;
        }
        QMenu::item {
            padding: 8px 20px;
        }
        QMenu::item:selected {
            background-color: #16a34a;
        }
        """)

        self.apply_styles()
        self.update_navbar()

    # ===== STYLE =====
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
            font-size: 20px;
        }

        QPushButton:hover {
            text-decoration: underline;
        }

        QScrollBar:vertical {
            background: #1f2937;
            width: 10px;
            border-radius: 5px;
        }

        QScrollBar::handle:vertical {
            background: #16a34a;
            border-radius: 5px;
        }

        QScrollBar::handle:vertical:hover {
            background: #22c55e;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
        """)

    # ===== NAVIGATION =====
    def go_to_home(self):
        self.stack.setCurrentWidget(self.home_page)

    def go_to_trailers(self):
        if hasattr(self.trailer_page, "refresh"):
            self.trailer_page.refresh()
        self.stack.setCurrentWidget(self.trailer_page)

    def open_bookings(self):
        self.booking_page.load_data()
        self.stack.setCurrentWidget(self.booking_page)

    def open_my_bookings(self):
        self.my_bookings_page.load_data()
        self.stack.setCurrentWidget(self.my_bookings_page)

    def open_users(self):
        self.user_page.load_data()
        self.stack.setCurrentWidget(self.user_page)

    def open_favorites(self):
        self.favorite_page.load_data()
        self.stack.setCurrentWidget(self.favorite_page)

    def open_cart(self):
        self.cart_page.load_data()
        self.stack.setCurrentWidget(self.cart_page)

    def open_profile(self):
        self.profile_page.load_user()
        self.stack.setCurrentWidget(self.profile_page)

    def open_technical(self):
        self.technical_page.load_data()
        self.stack.setCurrentWidget(self.technical_page)

    def open_statistics(self):
        self.statistics_page.refresh_data()
        self.stack.setCurrentWidget(self.statistics_page)

    # ===== MENU =====
    def toggle_menu(self):
        self.menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))

    # ===== NAVBAR =====
    def update_navbar(self):
        while self.nav_layout.count():
            item = self.nav_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # LOGO
        logo_btn = QPushButton("PótkocsiPont")
        logo_btn.setStyleSheet("font-weight: bold; font-size: 20px;")
        logo_btn.clicked.connect(self.go_to_home)

        self.nav_layout.addWidget(logo_btn)
        self.nav_layout.addSpacing(40)

        # ALAP MENÜ
        home_btn = QPushButton("Főoldal")
        trailers_btn = QPushButton("Utánfutó foglalás")

        home_btn.clicked.connect(self.go_to_home)
        trailers_btn.clicked.connect(self.go_to_trailers)

        self.nav_layout.addWidget(home_btn)
        self.nav_layout.addWidget(trailers_btn)
        self.nav_layout.addStretch()

        session = SessionManager.instance()

        # ===== NEM LOGIN =====
        if not session.is_authenticated():
            reg_btn = QPushButton("Regisztráció")
            reg_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.register_page))

            login_btn = QPushButton("Belépés")
            login_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.login_page))

            self.nav_layout.addWidget(reg_btn)
            self.nav_layout.addWidget(login_btn)
            return

        user = session.get_user()
        role = user.role if user else None

        # ===== AVATAR =====
        avatar_btn = QPushButton()
        avatar_btn.setFixedSize(40, 40)
        avatar_btn.setCursor(Qt.PointingHandCursor)
        avatar_btn.clicked.connect(self.open_profile)

        if user and getattr(user, "profile_image_path", None):
            avatar = create_round_avatar(user.profile_image_path, 40)
            avatar_btn.setIcon(avatar)
            avatar_btn.setIconSize(avatar_btn.size())

        self.nav_layout.addWidget(avatar_btn)

        # ===== HAMBURGER =====
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setFixedSize(36, 36)
        self.menu_btn.clicked.connect(self.toggle_menu)

        self.nav_layout.addWidget(self.menu_btn)

        # ===== MENU ITEMS =====
        self.menu.clear()

        if role in ["admin", "employee"]:
            self.menu.addAction("Foglalások", self.open_bookings)
            self.menu.addAction("Utánfutók", self.open_technical)

        if role == "admin":
            self.menu.addAction("Felhasználók", self.open_users)
            self.menu.addAction("Statisztika", self.open_statistics)

        self.menu.addAction("Kedvencek", self.open_favorites)

        if role == "user":
            self.menu.addAction("Foglalásaim", self.open_my_bookings)
            self.menu.addAction("Kosár", self.open_cart)

        # ===== JOBB OLDAL =====
        profile_btn = QPushButton("Adataim")
        profile_btn.clicked.connect(self.open_profile)
        self.nav_layout.addWidget(profile_btn)

        logout_btn = QPushButton("Kilépés")
        logout_btn.clicked.connect(self.handle_logout)
        self.nav_layout.addWidget(logout_btn)

    # ===== LOGOUT =====
    def handle_logout(self):
        SessionManager.instance().logout()
        self.update_navbar()
        self.go_to_home()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())