from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt

from viewmodels.login_vm import LoginViewModel
from core.session_manager import SessionManager


class LoginView(QWidget):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.viewmodel = LoginViewModel()

        self.setMinimumWidth(350)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        title = QLabel("Bejelentkezés")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Jelszó")
        self.password_input.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("Belépés")
        login_button.clicked.connect(self.handle_login)

        layout.addWidget(title)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)

        self.setLayout(layout)

        self.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #ccc;
            }
            QPushButton {
                background-color: #10a64a;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0d8a3e;
            }
        """)

    # =========================
    # LOGIN LOGIKA
    # =========================
    def handle_login(self):

        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Hiba", "Minden mező kitöltése kötelező!")
            return

        success, user = self.viewmodel.login(email, password)

        if success:
            # Session mentés
            SessionManager.instance().login(user)

            QMessageBox.information(
                self,
                "Siker",
                f"Sikeres bejelentkezés!\nSzerepkör: {user.role}"
            )

            # Navbar frissítés
            self.main_window.update_navbar()

            # Vissza főoldalra
            self.main_window.stack.setCurrentWidget(
                self.main_window.home_page
            )

            # Mezők ürítése
            self.email_input.clear()
            self.password_input.clear()

        else:
            QMessageBox.warning(
                self,
                "Hiba",
                "Hibás email vagy jelszó!"
            )