from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QLabel, QFileDialog
)
from PySide6.QtCore import Qt
from database import SessionLocal
from models.user import User
from passlib.hash import bcrypt
from core.image_utils import create_round_avatar
from core.toast import Toast


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
        if not self.email.text().strip():
            toast = Toast(self.main_window, "Az email megadása kötelező!", success=False)
            toast.show_toast()
            return

        if not self.password.text().strip():
            toast = Toast(self.main_window, "A jelszó megadása kötelező!", success=False)
            toast.show_toast()
            return

        session = SessionLocal()

        # EMAIL ELLENŐRZÉS
        existing_user = session.query(User).filter_by(
            email=self.email.text().strip()
        ).first()

        if existing_user:
            toast = Toast(self.main_window, "Az email már létezik!", success=False)
            toast.show_toast()
            session.close()
            return

        user = User(
            first_name=self.first_name.text().strip(),
            last_name=self.last_name.text().strip(),
            email=self.email.text().strip(),
            password_hash=bcrypt.hash(self.password.text()),
            phone=self.phone.text().strip(),
            country=self.country.text().strip(),
            zip_code=self.zip_code.text().strip(),
            city=self.city.text().strip(),
            street=self.street.text().strip(),
            house_number=self.house_number.text().strip(),
            profile_image_path=self.avatar_path,
            role="user"
        )

        session.add(user)
        session.commit()
        session.close()

        saved_email = self.email.text().strip()

        toast = Toast(self.main_window, "Sikeres regisztráció!", success=True)
        toast.show_toast()

        # Átváltás login oldalra
        self.main_window.stack.setCurrentWidget(self.main_window.login_page)

        # Email automatikus kitöltése login mezőben
        self.main_window.login_page.email.setText(saved_email)

        # Jelszó mező ürítése biztonság miatt
        self.main_window.login_page.password.clear()


        # Űrlap törlése
        self.first_name.clear()
        self.last_name.clear()
        self.email.clear()
        self.password.clear()
        self.phone.clear()
        self.country.clear()
        self.zip_code.clear()
        self.city.clear()
        self.street.clear()
        self.house_number.clear()
        self.avatar_preview.clear()
        self.avatar_path = None