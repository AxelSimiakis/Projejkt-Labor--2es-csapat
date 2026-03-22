from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout
)

from database import SessionLocal
from models.user import User
from core.session_manager import SessionManager
from core.toast import Toast


class UserView(QWidget):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Email", "Név", "Role", "Művelet"
        ])

        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        session = SessionLocal()
        users = session.query(User).all()

        self.table.setRowCount(len(users))

        current_user = SessionManager.instance().get_user()

        for row, u in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(u.email))
            self.table.setItem(row, 1, QTableWidgetItem(f"{u.first_name} {u.last_name}"))
            self.table.setItem(row, 2, QTableWidgetItem(u.role))

            delete_btn = QPushButton("Törlés")
            delete_btn.clicked.connect(lambda _, uid=u.id: self.delete_user(uid))

            container = QHBoxLayout()
            container.addWidget(delete_btn)

            widget = QWidget()
            widget.setLayout(container)

            self.table.setCellWidget(row, 3, widget)

        session.close()

    def delete_user(self, user_id):

        current = SessionManager.instance().get_user()

        if current.id == user_id:
            Toast(self.main_window, "Saját magad nem törölheted!", False).show_toast()
            return

        session = SessionLocal()
        user = session.get(User, user_id)

        session.delete(user)
        session.commit()
        session.close()

        Toast(self.main_window, "Felhasználó törölve", True).show_toast()
        self.load_data()