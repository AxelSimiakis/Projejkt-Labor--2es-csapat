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


        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.trailer_page)
        self.stack.addWidget(self.register_page)
        self.stack.addWidget(self.profile_page)
        self.stack.addWidget(self.booking_page)
        self.stack.addWidget(self.user_page)

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
        self.trailer_page.refresh()
        self.stack.setCurrentWidget(self.trailer_page)

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
        trailers_btn = QPushButton("Utánfutók")

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
        else:
            user = session.get_user()
            role = user.role

            avatar_btn = QPushButton()
            avatar_btn.setFixedSize(40, 40)
            avatar_btn.setCursor(Qt.PointingHandCursor)
            avatar_btn.setStyleSheet("""
                border-radius: 20px;
                border: none;
            """)
            avatar_btn.clicked.connect(self.open_profile)

            if user and user.profile_image_path:
                avatar = create_round_avatar(user.profile_image_path, 40)
                avatar_btn.setIcon(avatar)
                avatar_btn.setIconSize(avatar_btn.size())

            self.nav_layout.addWidget(avatar_btn)

            # ===== ADMIN / EMPLOYEE GOMBOK =====
            if role in ["admin", "employee"]:
                bookings_btn = QPushButton("Foglalások")
                bookings_btn.clicked.connect(self.open_bookings)
                self.nav_layout.addWidget(bookings_btn)

            if role == "admin":
                users_btn = QPushButton("Felhasználók")
                users_btn.clicked.connect(self.open_users)
                self.nav_layout.addWidget(users_btn)

            # ===== ALAP GOMBOK =====
            profile_btn = QPushButton("Adataim")
            profile_btn.clicked.connect(self.open_profile)
            self.nav_layout.addWidget(profile_btn)

            logout_btn = QPushButton("Kilépés")
            logout_btn.clicked.connect(self.handle_logout)
            self.nav_layout.addWidget(logout_btn)
    
    
    def open_bookings(self):
        self.booking_page.load_data()
        self.stack.setCurrentWidget(self.booking_page)

    def open_users(self):
        self.user_page.load_data()
        self.stack.setCurrentWidget(self.user_page)

    def open_profile(self):
        self.profile_page.load_user()
        self.stack.setCurrentWidget(self.profile_page)

    def handle_logout(self):
        SessionManager.instance().logout()
        self.trailer_page.refresh()
        self.update_navbar()
        self.go_to_home()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())