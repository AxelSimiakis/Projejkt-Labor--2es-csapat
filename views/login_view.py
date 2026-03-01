from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton,
    QFrame
)
from PySide6.QtCore import Qt

from viewmodels.login_vm import LoginViewModel
from core.session_manager import SessionManager
from core.toast import Toast

class LoginView(QWidget):

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.vm = LoginViewModel()

        outer_layout = QVBoxLayout()
        outer_layout.addStretch()

        # ===== KÁRTYA PANEL =====
        self.card = QFrame()
        self.card.setFixedWidth(400)
        self.card.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 12px;
                padding: 25px;
            }

            QLineEdit {
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #ccc;
            }

            QPushButton#mainButton {
                background-color: #16a34a;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }

            QPushButton#mainButton:hover {
                background-color: #15803d;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        title = QLabel("Bejelentkezés")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Jelszó")
        self.password.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("Belépés")
        login_btn.setObjectName("mainButton")
        login_btn.clicked.connect(self.handle_login)

        layout.addWidget(title)
        layout.addWidget(self.email)
        layout.addWidget(self.password)
        layout.addSpacing(10)
        layout.addWidget(login_btn)

        self.card.setLayout(layout)

        outer_layout.addWidget(self.card, alignment=Qt.AlignCenter)
        outer_layout.addStretch()

        self.setLayout(outer_layout)

    # =====================
    # LOGIN LOGIKA
    # =====================
    def handle_login(self):

        success, user = self.vm.login(
            self.email.text(),
            self.password.text()
        )

        if success:
            SessionManager.instance().login(user)
            toast = Toast(self.main_window, "Sikeres bejelentkezés!", success=True)
            toast.show_toast()

            self.main_window.update_navbar()
            self.main_window.stack.setCurrentIndex(0)
        else:
            toast = Toast(self.main_window, "Hibás email vagy jelszó!", success=False)
            toast.show_toast()