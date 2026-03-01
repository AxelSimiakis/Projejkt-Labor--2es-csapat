from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QFileDialog, QGridLayout
)
from PySide6.QtCore import Qt
from core.session_manager import SessionManager
from core.image_utils import create_round_avatar
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

        # ===== AVATAR =====
        left = QVBoxLayout()
        left.setAlignment(Qt.AlignCenter)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(150, 150)

        left.addWidget(self.avatar_label)

        self.avatar_btn = QPushButton("Profilkép cseréje")
        self.avatar_btn.clicked.connect(self.change_avatar)
        left.addWidget(self.avatar_btn)

        # ===== ADATOK =====
        right = QGridLayout()
        right.setSpacing(15)

        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()

        self.country = QLineEdit()
        self.zip_code = QLineEdit()
        self.city = QLineEdit()
        self.street = QLineEdit()
        self.house_number = QLineEdit()

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

    def change_avatar(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Profilkép", "", "Images (*.png *.jpg *.jpeg)"
        )
        if not path:
            return

        session = SessionLocal()
        user = session.query(User).filter_by(
            id=SessionManager.instance().get_user().id
        ).first()

        user.profile_image_path = path
        session.commit()
        session.close()

        SessionManager.instance()._user.profile_image_path = path

        self.load_user()
        self.main_window.update_navbar()

    def save_changes(self):
        session = SessionLocal()
        current = SessionManager.instance().get_user()

        user = session.query(User).filter_by(id=current.id).first()

        user.first_name = self.first_name.text()
        user.last_name = self.last_name.text()
        user.phone = self.phone.text()
        user.country = self.country.text()
        user.zip_code = self.zip_code.text()
        user.city = self.city.text()
        user.street = self.street.text()
        user.house_number = self.house_number.text()

        session.commit()
        session.close()