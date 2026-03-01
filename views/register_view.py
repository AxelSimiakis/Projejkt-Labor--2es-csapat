from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QLabel, QFileDialog
)
from PySide6.QtCore import Qt
from database import SessionLocal
from models.user import User
from passlib.hash import bcrypt
from core.image_utils import create_round_avatar


class RegisterView(QWidget):

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.avatar_path = None

        container = QVBoxLayout()
        container.setAlignment(Qt.AlignCenter)

        self.card = QWidget()
        self.card.setFixedWidth(500)
        self.card.setStyleSheet("""
            background-color: #1f2937;
            border-radius: 15px;
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        # ===== AVATAR PREVIEW =====
        self.avatar_preview = QLabel()
        self.avatar_preview.setFixedSize(120, 120)
        self.avatar_preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.avatar_preview, alignment=Qt.AlignCenter)

        self.avatar_btn = QPushButton("Profilkép kiválasztása")
        self.avatar_btn.clicked.connect(self.select_avatar)
        layout.addWidget(self.avatar_btn)

        # ===== ADATOK =====
        self.first_name = QLineEdit()
        self.first_name.setPlaceholderText("Vezetéknév")

        self.last_name = QLineEdit()
        self.last_name.setPlaceholderText("Keresztnév")

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Jelszó")
        self.password.setEchoMode(QLineEdit.Password)

        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Telefon")

        self.country = QLineEdit()
        self.country.setPlaceholderText("Ország")

        self.zip_code = QLineEdit()
        self.zip_code.setPlaceholderText("Irányítószám")

        self.city = QLineEdit()
        self.city.setPlaceholderText("Város")

        self.street = QLineEdit()
        self.street.setPlaceholderText("Utca")

        self.house_number = QLineEdit()
        self.house_number.setPlaceholderText("Házszám")

        fields = [
            self.first_name, self.last_name,
            self.email, self.password,
            self.phone, self.country,
            self.zip_code, self.city,
            self.street, self.house_number
        ]

        for field in fields:
            field.setStyleSheet("padding:8px; border-radius:6px;")
            layout.addWidget(field)

        self.register_btn = QPushButton("Regisztráció")
        self.register_btn.setStyleSheet("""
            background-color: #16a34a;
            color: white;
            padding: 10px;
            border-radius: 6px;
        """)
        self.register_btn.clicked.connect(self.register_user)

        layout.addWidget(self.register_btn)

        self.card.setLayout(layout)
        container.addWidget(self.card)
        self.setLayout(container)

    def select_avatar(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Profilkép", "", "Images (*.png *.jpg *.jpeg)"
        )
        if path:
            self.avatar_path = path
            avatar = create_round_avatar(path, 120)
            self.avatar_preview.setPixmap(avatar)

    def register_user(self):
        session = SessionLocal()

        user = User(
            first_name=self.first_name.text(),
            last_name=self.last_name.text(),
            email=self.email.text(),
            password_hash=bcrypt.hash(self.password.text()),
            phone=self.phone.text(),
            country=self.country.text(),
            zip_code=self.zip_code.text(),
            city=self.city.text(),
            street=self.street.text(),
            house_number=self.house_number.text(),
            profile_image_path=self.avatar_path,
            role="user"
        )

        session.add(user)
        session.commit()
        session.close()

        self.main_window.update_navbar()