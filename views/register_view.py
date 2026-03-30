from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QLabel, QFileDialog
)
from PySide6.QtGui import QIntValidator, QRegularExpressionValidator
from PySide6.QtCore import Qt, QRegularExpression

from database import SessionLocal
from models.user import User
from passlib.hash import bcrypt
from core.image_utils import create_round_avatar
from core.toast import Toast
from services.email_service import send_registration_email


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

        # ===== VALIDÁTOROK =====
        text_regex = QRegularExpression("^[A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű ]+$")
        text_validator = QRegularExpressionValidator(text_regex)

        number_validator = QIntValidator()

        phone_regex = QRegularExpression(r"^\+\d{2} \d{2} \d{3} \d{4}$")
        phone_validator = QRegularExpressionValidator(phone_regex)

        # ===== AVATAR =====
        self.avatar_preview = QLabel()
        self.avatar_preview.setFixedSize(120, 120)
        self.avatar_preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.avatar_preview, alignment=Qt.AlignCenter)

        self.avatar_btn = QPushButton("Profilkép kiválasztása")
        self.avatar_btn.clicked.connect(self.select_avatar)
        layout.addWidget(self.avatar_btn)

        # ===== INPUTOK =====
        def create_input(placeholder):
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            field.setStyleSheet("padding:8px; border-radius:6px;")
            return field

        self.first_name = create_input("Vezetéknév")
        self.last_name = create_input("Keresztnév")
        self.email = create_input("Email")
        self.password = create_input("Jelszó")
        self.password.setEchoMode(QLineEdit.Password)

        self.phone = create_input("Telefonszám +36 70 000 0000")

        self.country = create_input("Ország")
        self.zip_code = create_input("Irányítószám")
        self.city = create_input("Város")
        self.street = create_input("Utca")
        self.house_number = create_input("Házszám")

        # ===== VALIDÁTOROK HOZZÁADÁSA =====
        for f in [self.first_name, self.last_name, self.country, self.city, self.street]:
            f.setValidator(text_validator)

        for f in [self.zip_code, self.house_number]:
            f.setValidator(number_validator)

        self.phone.setValidator(phone_validator)

        # ===== MAX LENGTH =====
        self.first_name.setMaxLength(50)
        self.last_name.setMaxLength(50)
        self.country.setMaxLength(50)
        self.city.setMaxLength(50)
        self.street.setMaxLength(100)

        self.zip_code.setMaxLength(4)
        self.house_number.setMaxLength(10)
        self.phone.setMaxLength(16)

        fields = [
            self.first_name, self.last_name,
            self.email, self.password,
            self.phone, self.country,
            self.zip_code, self.city,
            self.street, self.house_number
        ]

        for field in fields:
            layout.addWidget(field)

        # ===== REGISZTRÁCIÓ GOMB =====
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

    # ===== AVATAR =====
    def select_avatar(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Profilkép", "", "Images (*.png *.jpg *.jpeg)"
        )
        if path:
            self.avatar_path = path
            avatar = create_round_avatar(path, 120)
            self.avatar_preview.setPixmap(avatar)

    # ===== REGISZTRÁCIÓ =====
    def register_user(self):

        # TELEFON VALIDÁCIÓ
        if not self.phone.hasAcceptableInput():
            Toast(self.main_window, "Hibás telefonszám! (+XX XX XXX XXXX)", success=False).show_toast()
            return

        if not self.email.text().strip():
            Toast(self.main_window, "Az email megadása kötelező!", success=False).show_toast()
            return

        if not self.password.text().strip():
            Toast(self.main_window, "A jelszó megadása kötelező!", success=False).show_toast()
            return

        plain_password = self.password.text().strip()

        session = SessionLocal()

        try:
            # EMAIL ELLENŐRZÉS
            existing_user = session.query(User).filter_by(
                email=self.email.text().strip()
            ).first()

            if existing_user:
                Toast(self.main_window, "Az email már létezik!", success=False).show_toast()
                return

            # USER LÉTREHOZÁS
            user = User(
                first_name=self.first_name.text().strip(),
                last_name=self.last_name.text().strip(),
                email=self.email.text().strip(),
                password_hash=bcrypt.hash(plain_password),
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

        except Exception as e:
            session.rollback()
            Toast(self.main_window, f"Hiba regisztráció közben: {e}", success=False).show_toast()
            return
        finally:
            session.close()

        saved_email = self.email.text().strip()
        full_name = f"{self.first_name.text().strip()} {self.last_name.text().strip()}".strip()

        try:
            send_registration_email(
                email=saved_email,
                name=full_name,
                password=plain_password
            )
        except Exception as e:
            print("EMAIL HIBA (regisztráció után):", e)

        Toast(self.main_window, "Sikeres regisztráció!", success=True).show_toast()

        # ÁTVÁLT LOGINRA
        self.main_window.stack.setCurrentWidget(self.main_window.login_page)

        self.main_window.login_page.email.setText(saved_email)
        self.main_window.login_page.password.clear()

        # ŰRLAP törlés
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