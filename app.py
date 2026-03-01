import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QLabel
)
from PySide6.QtCore import Qt

from views.home_view import HomeView
from views.login_view import LoginView
from views.trailer_list_view import TrailerListView
from views.register_view import RegisterView
from views.profile_view import ProfileView
from core.session_manager import SessionManager
from core.image_utils import create_round_avatar
from core.toast import Toast


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
        self.nav_layout.setSpacing(25)
        self.navbar.setLayout(self.nav_layout)

        self.main_layout.addWidget(self.navbar)

        # ===== STACK =====
        self.stack = QStackedWidget()

        self.home_page = HomeView()
        self.login_page = LoginView(self)
        self.trailer_page = TrailerListView()
        self.register_page = RegisterView(self)
        self.profile_page = ProfileView(self)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.trailer_page)
        self.stack.addWidget(self.register_page)
        self.stack.addWidget(self.profile_page)

        self.main_layout.addWidget(self.stack)

        main_widget.setLayout(self.main_layout)
        self.setCentralWidget(main_widget)

        self.apply_styles()
        self.update_navbar()

    # =========================
    # STÍLUS
    # =========================
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
            font-size: 15px;
        }

        QPushButton:hover {
            text-decoration: underline;
        }
        """)

    # =========================
    # NAVBAR FRISSÍTÉS
    # =========================
    def update_navbar(self):

        # régi elemek törlése
        while self.nav_layout.count():
            item = self.nav_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # ---- Bal oldal ----
        logo_btn = QPushButton("PótkocsiPont")
        logo_btn.setStyleSheet("font-weight: bold; font-size: 18px;")
        logo_btn.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.home_page)
        )

        home_btn = QPushButton("Főoldal")
        trailers_btn = QPushButton("Utánfutók")

        home_btn.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.home_page)
        )
        trailers_btn.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.trailer_page)
        )

        self.nav_layout.addWidget(logo_btn)
        self.nav_layout.addSpacing(40)
        self.nav_layout.addWidget(home_btn)
        self.nav_layout.addWidget(trailers_btn)
        self.nav_layout.addStretch()

        session = SessionManager.instance()

        # ===== NINCS BEJELENTKEZVE =====
        if not session.is_authenticated():

            register_btn = QPushButton("Regisztráció")
            register_btn.clicked.connect(
                lambda: self.stack.setCurrentWidget(self.register_page)
            )

            login_btn = QPushButton("Belépés")
            login_btn.clicked.connect(
                lambda: self.stack.setCurrentWidget(self.login_page)
            )

            self.nav_layout.addWidget(register_btn)
            self.nav_layout.addWidget(login_btn)

        # ===== BEJELENTKEZVE =====
        else:
            user = session.get_user()

            # ---- Profilkép (kattintható) ----
            avatar_btn = QPushButton()
            avatar_btn.setFixedSize(40, 40)
            avatar_btn.setCursor(Qt.PointingHandCursor)
            avatar_btn.setStyleSheet("""
                border-radius: 20px;
                border: none;
            """)
            avatar_btn.clicked.connect(self.open_profile)

            if user and user.profile_image_path:
                avatar = create_round_avatar(
                    user.profile_image_path,
                    40
                )
                avatar_btn.setIcon(avatar)
                avatar_btn.setIconSize(avatar_btn.size())

            self.nav_layout.addWidget(avatar_btn)

            # ---- Adataim ----
            profile_btn = QPushButton("Adataim")
            profile_btn.clicked.connect(self.open_profile)
            self.nav_layout.addWidget(profile_btn)

            # ---- Kilépés ----
            logout_btn = QPushButton("Kilépés")
            logout_btn.clicked.connect(self.handle_logout)
            self.nav_layout.addWidget(logout_btn)

    # =========================
    # PROFIL MEGNYITÁS
    # =========================
    def open_profile(self):
        self.profile_page.load_user()
        self.stack.setCurrentWidget(self.profile_page)

    # =========================
    # LOGOUT
    # =========================
    def handle_logout(self):
        SessionManager.instance().logout()
        self.update_navbar()
        self.stack.setCurrentWidget(self.home_page)


# =========================
# INDÍTÁS
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())