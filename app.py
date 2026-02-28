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
from core.session_manager import SessionManager


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PótkocsiPont")
        self.setMinimumSize(1000, 650)

        # ===== FŐ LAYOUT =====
        main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # ===== NAVBAR =====
        self.navbar = QWidget()
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(20, 0, 20, 0)
        self.navbar.setLayout(self.nav_layout)
        self.navbar.setFixedHeight(60)

        self.navbar.setStyleSheet("""
            QWidget {
                background-color: #10a64a;
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

        self.main_layout.addWidget(self.navbar)

        # ===== STACK =====
        self.stack = QStackedWidget()

        self.home_page = HomeView()
        self.login_page = LoginView(self)
        self.trailer_page = TrailerListView()

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.trailer_page)

        self.main_layout.addWidget(self.stack)

        main_widget.setLayout(self.main_layout)
        self.setCentralWidget(main_widget)

        # Első navbar betöltés
        self.update_navbar()

    # =========================
    # NAVBAR FRISSÍTÉS
    # =========================
    def update_navbar(self):

        # Előző gombok törlése
        while self.nav_layout.count():
            item = self.nav_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Alap gombok
        home_btn = QPushButton("Főoldal")
        trailers_btn = QPushButton("Utánfutók")

        home_btn.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.home_page)
        )
        trailers_btn.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.trailer_page)
        )

        self.nav_layout.addWidget(home_btn)
        self.nav_layout.addWidget(trailers_btn)
        self.nav_layout.addStretch()

        session = SessionManager.instance()

        # ===== NINCS BEJELENTKEZVE =====
        if not session.is_authenticated():
            login_btn = QPushButton("Belépés")
            login_btn.clicked.connect(
                lambda: self.stack.setCurrentWidget(self.login_page)
            )
            self.nav_layout.addWidget(login_btn)

        # ===== BEJELENTKEZVE =====
        else:
            role = session.get_role()

            # Admin panel
            if role == "admin":
                admin_btn = QPushButton("Admin panel")
                self.nav_layout.addWidget(admin_btn)

            # Employee vagy Admin
            if role in ["admin", "employee"]:
                employee_btn = QPushButton("Foglalások")
                self.nav_layout.addWidget(employee_btn)

            logout_btn = QPushButton("Kilépés")
            logout_btn.clicked.connect(self.handle_logout)
            self.nav_layout.addWidget(logout_btn)

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
    window = MainWindow()
    window.show()
    sys.exit(app.exec())