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

        # ===== HEADER =====
        top = QHBoxLayout()

        title = QLabel("Felhasználók")
        title.setStyleSheet("color:white; font-size:18px; font-weight:bold;")

        add_btn = QPushButton("+ Új felhasználó")
        add_btn.clicked.connect(self.create_user)

        top.addWidget(title)
        top.addStretch()
        top.addWidget(add_btn)

        layout.addLayout(top)

        # ===== TABLE =====
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
        self.table.verticalHeader().setVisible(False)

        self.table.verticalHeader().setDefaultSectionSize(50)
        
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_data()

    # ======================
    # LOAD
    # ======================
    def load_data(self):
        session = SessionLocal()
        users = session.query(User).all()

        header = self.table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 220)

        self.table.setRowCount(len(users))

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

            # ===== GOMBOK =====
            edit_btn = QPushButton("Szerkesztés")
            edit_btn.setFixedHeight(30)
            edit_btn.setMinimumWidth(100)
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
            delete_btn.setFixedHeight(30)
            delete_btn.setMinimumWidth(80)
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
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(8)

            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 9, container)

        session.close()

    # ======================
    # DELETE
    # ======================
    def delete_user(self, user_id):
        session = SessionLocal()
        user = session.get(User, user_id)

        if user:
            session.delete(user)
            session.commit()

        session.close()
        Toast(self.main_window, "Felhasználó törölve", False).show_toast()
        self.load_data()

    # ======================
    # CREATE
    # ======================
    def create_user(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Új felhasználó")
        dialog.setStyleSheet("background-color:#1f2937; color:white;")

        layout = QFormLayout()

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
        save.setStyleSheet("""
        QPushButton {
            background-color: #16a34a;
            color: white;
        }
        QPushButton:hover {
            background-color: #15803d;
        }
        """)

        cancel = QPushButton("Mégse")
        cancel.setStyleSheet("""
        QPushButton {
            background-color: #374151;
            color: white;
        }
        QPushButton:hover {
            background-color: #4b5563;
        }
        """)

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

    # ======================
    # EDIT
    # ======================
    def edit_user(self, user_id):
        session = SessionLocal()
        user = session.get(User, user_id)

        dialog = QDialog(self)
        dialog.setWindowTitle("Felhasználó szerkesztése")
        dialog.setStyleSheet("""
        QDialog {
            background-color: #1f2937;
            color: white;
            border-radius: 12px;
        }

        QLabel {
            color: #d1d5db;
        }

        QComboBox, QDateEdit {
            background-color: #111827;
            color: white;
            padding: 6px;
            border-radius: 6px;
            border: 1px solid #374151;
        }

        QPushButton {
            border-radius: 8px;
            padding: 8px;
        }
        """)


        layout = QFormLayout()

        first = QLineEdit(user.first_name)
        last = QLineEdit(user.last_name)
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
        layout.addRow("Telefon:", phone)
        layout.addRow("Ország:", country)
        layout.addRow("Város:", city)
        layout.addRow("Utca:", street)
        layout.addRow("Házszám:", house)
        layout.addRow("Irányítószám:", zip_code)
        layout.addRow("Szerepkör:", role)

        save = QPushButton("Mentés")
        save.setStyleSheet("""
        QPushButton {
            background-color: #16a34a;
            color: white;
        }
        QPushButton:hover {
            background-color: #15803d;
        }
        """)

        def do_save():
            user.first_name = first.text()
            user.last_name = last.text()
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

        layout.addRow(save)
        dialog.setLayout(layout)
        dialog.exec()