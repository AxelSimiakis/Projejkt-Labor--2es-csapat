from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QFileDialog, QGridLayout
)
from PySide6.QtGui import QIntValidator, QRegularExpressionValidator
from PySide6.QtCore import Qt, QRegularExpression

from core.session_manager import SessionManager
from core.image_utils import create_round_avatar
from core.toast import Toast

from database import SessionLocal
from models.user import User


class ProfileView(QWidget):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        container = QVBoxLayout()
        container.setAlignment(Qt.AlignCenter)

        self.card = QWidget()
        self.card.setFixedWidth(900)
        self.card.setStyleSheet("""
            background-color: #1f2937;
            border-radius: 15px;
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(60)

        # ======================
        # VALIDÁTOROK
        # ======================

        text_regex = QRegularExpression("^[A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű ]+$")
        text_validator = QRegularExpressionValidator(text_regex)

        number_validator = QIntValidator()

        phone_regex = QRegularExpression(r"^\+\d{2} \d{2} \d{3} \d{4}$")
        phone_validator = QRegularExpressionValidator(phone_regex)

        # ======================
        # AVATAR
        # ======================

        left = QVBoxLayout()
        left.setAlignment(Qt.AlignCenter)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(150, 150)

        left.addWidget(self.avatar_label)

        self.avatar_btn = QPushButton("Profilkép cseréje")
        self.avatar_btn.clicked.connect(self.change_avatar)
        left.addWidget(self.avatar_btn)

        # ======================
        # ADATOK
        # ======================

        right = QGridLayout()
        right.setSpacing(15)

        def create_input(placeholder=""):
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            field.setStyleSheet("padding:8px; border-radius:6px;")
            return field

        self.first_name = create_input("Vezetéknév")
        self.last_name = create_input("Keresztnév")
        self.email = create_input("Email")
        self.phone = create_input("Telefonszám: +36 70 000 0000")

        self.country = create_input("Ország")
        self.zip_code = create_input("Irányítószám")
        self.city = create_input("Város")
        self.street = create_input("Utca")
        self.house_number = create_input("Házszám")

        # ===== VALIDÁTOROK =====
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
            ("Vezetéknév:", self.first_name),
            ("Keresztnév:", self.last_name),
            ("Email:", self.email),
            ("Telefon:", self.phone),
            ("Ország:", self.country),
            ("Irányítószám:", self.zip_code),
            ("Város:", self.city),
            ("Utca:", self.street),
            ("Házszám:", self.house_number),
        ]

        for row, (label, widget) in enumerate(fields):
            right.addWidget(QLabel(label), row, 0)
            right.addWidget(widget, row, 1)

        self.save_btn = QPushButton("Mentés")
        self.save_btn.setStyleSheet("""
            background-color: #16a34a;
            color: white;
            padding: 10px;
            border-radius: 6px;
        """)
        self.save_btn.clicked.connect(self.save_changes)

        right.addWidget(self.save_btn, len(fields), 0, 1, 2)

        layout.addLayout(left)
        layout.addLayout(right)

        self.card.setLayout(layout)
        container.addWidget(self.card)
        self.setLayout(container)

    # ======================
    # USER BETÖLTÉS
    # ======================

    def load_user(self):

        user = SessionManager.instance().get_user()

        if not user:
            return

        self.first_name.setText(user.first_name or "")
        self.last_name.setText(user.last_name or "")
        self.email.setText(user.email or "")
        self.phone.setText(user.phone or "")
        self.country.setText(user.country or "")
        self.zip_code.setText(user.zip_code or "")
        self.city.setText(user.city or "")
        self.street.setText(user.street or "")
        self.house_number.setText(user.house_number or "")

        if user.profile_image_path:
            avatar = create_round_avatar(user.profile_image_path, 150)
            self.avatar_label.setPixmap(avatar)

    # ======================
    # AVATAR CSERE
    # ======================

    def change_avatar(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Profilkép",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if not path:
            return

        session = SessionLocal()

        user = session.query(User).filter_by(
            id=SessionManager.instance().get_user().id
        ).first()

        user.profile_image_path = path
        session.commit()

        SessionManager.instance()._user.profile_image_path = path

        session.close()

        self.load_user()
        self.main_window.update_navbar()

        Toast(self.main_window, "Profilkép frissítve!", True).show_toast()

    # ======================
    # ADATOK MENTÉSE
    # ======================

    def save_changes(self):

        # TELEFON VALIDÁCIÓ
        if not self.phone.hasAcceptableInput():
            Toast(self.main_window, "Hibás telefonszám! (+XX XX XXX XXXX)", False).show_toast()
            return

        session = SessionLocal()
        current = SessionManager.instance().get_user()

        user = session.query(User).filter_by(id=current.id).first()

        if (
            user.first_name == self.first_name.text() and
            user.last_name == self.last_name.text() and
            user.phone == self.phone.text() and
            user.country == self.country.text() and
            user.zip_code == self.zip_code.text() and
            user.city == self.city.text() and
            user.street == self.street.text() and
            user.house_number == self.house_number.text()
        ):
            session.close()
            Toast(self.main_window, "Nincs módosítás.", False).show_toast()
            return

        # MENTÉS
        user.first_name = self.first_name.text()
        user.last_name = self.last_name.text()
        user.phone = self.phone.text()
        user.country = self.country.text()
        user.zip_code = self.zip_code.text()
        user.city = self.city.text()
        user.street = self.street.text()
        user.house_number = self.house_number.text()

        session.commit()

        # Session frissítés
        SessionManager.instance()._user.first_name = user.first_name
        SessionManager.instance()._user.last_name = user.last_name
        SessionManager.instance()._user.phone = user.phone
        SessionManager.instance()._user.country = user.country
        SessionManager.instance()._user.zip_code = user.zip_code
        SessionManager.instance()._user.city = user.city
        SessionManager.instance()._user.street = user.street
        SessionManager.instance()._user.house_number = user.house_number

        session.close()

        self.main_window.update_navbar()

        Toast(self.main_window, "Adatok sikeresen mentve!", True).show_toast()