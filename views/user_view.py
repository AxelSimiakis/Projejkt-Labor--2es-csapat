from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QComboBox, QLabel, QAbstractItemView
)
from PySide6.QtCore import Qt

from database import SessionLocal
from models.user import User
from core.toast import Toast
from passlib.hash import bcrypt


class UserView(QWidget):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        layout = QVBoxLayout()

        top = QHBoxLayout()

        title = QLabel("Felhasználók")
        title.setStyleSheet("color:white; font-size:18px; font-weight:bold;")

        add_btn = QPushButton("+ Új felhasználó")
        add_btn.clicked.connect(self.create_user)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
        QPushButton {
            background-color: #16a34a;
            color: white;
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 13px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #15803d;
        }
        """)

        top.addWidget(title)
        top.addStretch()
        top.addWidget(add_btn)

        layout.addLayout(top)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Név", "Email", "Telefon", "Szerepkör",
            "Ország", "Város", "Utca", "Házszám", "Irányítószám", "Művelet"
        ])

        self.table.setStyleSheet("""
        QTableWidget {
            background-color: #1f2937;
            color: white;
            gridline-color: #374151;
            border: none;
            border-radius: 10px;
        }

        QHeaderView::section {
            background-color: #111827;
            color: #9ca3af;
            padding: 8px;
            border: none;
        }

        QTableWidget::item {
            padding: 6px;
        }

        QTableWidget::item:selected {
            background-color: #16a34a;
        }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(56)
        self.table.setWordWrap(True)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_data()

    def _apply_dialog_style(self, dialog):
        dialog.setStyleSheet("""
        QDialog {
            background-color: #1f2937;
            color: white;
            border-radius: 12px;
        }

        QLabel {
            color: white;
            font-size: 13px;
            background: transparent;
        }

        QLineEdit, QComboBox {
            background-color: #111827;
            color: white;
            padding: 8px;
            border-radius: 8px;
            border: 1px solid #374151;
            min-height: 18px;
        }

        QLineEdit:focus, QComboBox:focus {
            border: 1px solid #16a34a;
        }

        QPushButton {
            border-radius: 8px;
            padding: 8px 12px;
            min-height: 18px;
        }
        """)

    def _primary_button_style(self):
        return """
        QPushButton {
            background-color: #16a34a;
            color: white;
            border: none;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #15803d;
        }
        """

    def _secondary_button_style(self):
        return """
        QPushButton {
            background-color: #374151;
            color: white;
            border: none;
        }
        QPushButton:hover {
            background-color: #4b5563;
        }
        """

    def load_data(self):
        session = SessionLocal()
        users = session.query(User).all()

        self.table.clearContents()
        self.table.setRowCount(len(users))

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.Stretch)            # Név
        header.setSectionResizeMode(1, QHeaderView.Stretch)            # Email
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)   # Telefon
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)   # Szerepkör
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)   # Ország
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)   # Város
        header.setSectionResizeMode(6, QHeaderView.Stretch)            # Utca
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)   # Házszám
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)   # Irányítószám
        header.setSectionResizeMode(9, QHeaderView.Fixed)              # Művelet

        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 110)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(7, 90)
        self.table.setColumnWidth(8, 100)
        self.table.setColumnWidth(9, 230)

        for row, u in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(f"{u.first_name} {u.last_name}"))
            self.table.setItem(row, 1, QTableWidgetItem(u.email))
            self.table.setItem(row, 2, QTableWidgetItem(u.phone or "-"))
            self.table.setItem(row, 3, QTableWidgetItem(u.role))
            self.table.setItem(row, 4, QTableWidgetItem(u.country or "-"))
            self.table.setItem(row, 5, QTableWidgetItem(u.city or "-"))
            self.table.setItem(row, 6, QTableWidgetItem(u.street or "-"))
            self.table.setItem(row, 7, QTableWidgetItem(u.house_number or "-"))
            self.table.setItem(row, 8, QTableWidgetItem(u.zip_code or "-"))

            edit_btn = QPushButton("Szerkesztés")
            edit_btn.setFixedHeight(32)
            edit_btn.setMinimumWidth(110)
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
            """)
            edit_btn.clicked.connect(lambda _, uid=u.id: self.edit_user(uid))

            delete_btn = QPushButton("Törlés")
            delete_btn.setFixedHeight(32)
            delete_btn.setMinimumWidth(90)
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #1f2937;
                color: #d1d5db;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #374151;
                color: white;
            }
            """)
            delete_btn.clicked.connect(lambda _, uid=u.id: self.delete_user(uid))

            container = QWidget()
            container.setStyleSheet("background: transparent;")

            btn_layout = QHBoxLayout(container)
            btn_layout.setContentsMargins(6, 0, 6, 0)
            btn_layout.setSpacing(8)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()

            self.table.setCellWidget(row, 9, container)

        session.close()

    def delete_user(self, user_id):
        from models.favorite import Favorite
        from models.cart_item import CartItem
        from models.booking import Booking

        session = SessionLocal()

        try:
            user = session.get(User, user_id)

            if not user:
                Toast(self.main_window, "A felhasználó nem található", False).show_toast()
                return

            # Előbb a kapcsolódó rekordok törlése
            session.query(Favorite).filter(Favorite.user_id == user_id).delete()
            session.query(CartItem).filter(CartItem.user_id == user_id).delete()
            session.query(Booking).filter(Booking.user_id == user_id).delete()

            # Utána maga a felhasználó
            session.delete(user)
            session.commit()

            Toast(self.main_window, "Felhasználó törölve", False).show_toast()
            self.load_data()

        except Exception as e:
            session.rollback()
            Toast(self.main_window, f"Hiba törlés közben: {e}", False).show_toast()
        finally:
            session.close()

    def create_user(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Új felhasználó")
        dialog.resize(420, 520)
        self._apply_dialog_style(dialog)

        layout = QFormLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        first = QLineEdit()
        last = QLineEdit()
        email = QLineEdit()
        phone = QLineEdit()
        country = QLineEdit()
        city = QLineEdit()
        street = QLineEdit()
        house = QLineEdit()
        zip_code = QLineEdit()
        password = QLineEdit()
        password.setEchoMode(QLineEdit.Password)

        role = QComboBox()
        role.addItems(["user", "employee", "admin"])

        layout.addRow("Vezetéknév:", first)
        layout.addRow("Keresztnév:", last)
        layout.addRow("Email:", email)
        layout.addRow("Telefon:", phone)
        layout.addRow("Ország:", country)
        layout.addRow("Város:", city)
        layout.addRow("Utca:", street)
        layout.addRow("Házszám:", house)
        layout.addRow("Irányítószám:", zip_code)
        layout.addRow("Jelszó:", password)
        layout.addRow("Szerepkör:", role)

        save = QPushButton("Mentés")
        save.setStyleSheet(self._primary_button_style())

        cancel = QPushButton("Mégse")
        cancel.setStyleSheet(self._secondary_button_style())

        btns = QHBoxLayout()
        btns.addWidget(save)
        btns.addWidget(cancel)

        layout.addRow(btns)
        dialog.setLayout(layout)

        def do_save():
            session = SessionLocal()

            new_user = User(
                first_name=first.text(),
                last_name=last.text(),
                email=email.text(),
                phone=phone.text(),
                country=country.text(),
                city=city.text(),
                street=street.text(),
                house_number=house.text(),
                zip_code=zip_code.text(),
                role=role.currentText(),
                password_hash=bcrypt.hash(password.text())
            )

            session.add(new_user)
            session.commit()
            session.close()

            Toast(self.main_window, "Felhasználó létrehozva", True).show_toast()

            dialog.accept()
            self.load_data()

        save.clicked.connect(do_save)
        cancel.clicked.connect(dialog.reject)

        dialog.exec()

    def edit_user(self, user_id):
        session = SessionLocal()
        user = session.get(User, user_id)

        if not user:
            session.close()
            Toast(self.main_window, "A felhasználó nem található", False).show_toast()
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Felhasználó szerkesztése")
        dialog.resize(420, 460)
        self._apply_dialog_style(dialog)

        layout = QFormLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        first = QLineEdit(user.first_name or "")
        last = QLineEdit(user.last_name or "")
        email = QLineEdit(user.email or "")
        phone = QLineEdit(user.phone or "")
        country = QLineEdit(user.country or "")
        city = QLineEdit(user.city or "")
        street = QLineEdit(user.street or "")
        house = QLineEdit(user.house_number or "")
        zip_code = QLineEdit(user.zip_code or "")

        role = QComboBox()
        role.addItems(["user", "employee", "admin"])
        role.setCurrentText(user.role)

        layout.addRow("Vezetéknév:", first)
        layout.addRow("Keresztnév:", last)
        layout.addRow("Email:", email)
        layout.addRow("Telefon:", phone)
        layout.addRow("Ország:", country)
        layout.addRow("Város:", city)
        layout.addRow("Utca:", street)
        layout.addRow("Házszám:", house)
        layout.addRow("Irányítószám:", zip_code)
        layout.addRow("Szerepkör:", role)

        save = QPushButton("Mentés")
        save.setStyleSheet(self._primary_button_style())

        cancel = QPushButton("Mégse")
        cancel.setStyleSheet(self._secondary_button_style())

        btns = QHBoxLayout()
        btns.addWidget(save)
        btns.addWidget(cancel)

        layout.addRow(btns)

        def do_save():
            user.first_name = first.text()
            user.last_name = last.text()
            user.email = email.text()
            user.phone = phone.text()
            user.country = country.text()
            user.city = city.text()
            user.street = street.text()
            user.house_number = house.text()
            user.zip_code = zip_code.text()
            user.role = role.currentText()

            session.commit()
            session.close()

            Toast(self.main_window, "Felhasználó frissítve", True).show_toast()

            dialog.accept()
            self.load_data()

        save.clicked.connect(do_save)
        cancel.clicked.connect(lambda: (session.close(), dialog.reject()))

        dialog.setLayout(layout)
        dialog.exec()