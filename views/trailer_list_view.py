from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QComboBox,
    QMessageBox,
    QDateEdit,
    QFrame,
)

from core.session_manager import SessionManager
from services.booking_service import (
    create_booking,
    get_availability_for_trailer_and_date,
)
from viewmodels.trailer_list_vm import TrailerListViewModel


class TrailerListView(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.viewmodel = TrailerListViewModel()
        self.trailers = []

        self.setWindowTitle("Elérhető utánfutók")
        self.setMinimumWidth(700)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        title = QLabel("Elérhető utánfutók")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        root.addWidget(title)

        content = QHBoxLayout()
        content.setSpacing(20)
        root.addLayout(content)

        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.on_trailer_selected)
        self.list_widget.setMinimumWidth(420)
        content.addWidget(self.list_widget, 2)

        right_panel = QFrame()
        right_panel.setStyleSheet(
            "QFrame { background-color: #1f2937; border-radius: 12px; padding: 12px; color: white; }"
        )
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(12)
        content.addWidget(right_panel, 3)

        self.image_label = QLabel()
        self.image_label.setFixedSize(320, 180)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #111827;
                border: 1px solid #374151;
                border-radius: 10px;
                color: #9ca3af;
            }
        """)
        self.image_label.setText("Nincs kép")
        right_layout.addWidget(self.image_label)

        self.name_label = QLabel("Válassz egy utánfutót")
        self.name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        right_layout.addWidget(self.name_label)

        self.description_label = QLabel("-")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #d1d5db;")
        right_layout.addWidget(self.description_label)

        self.price_label = QLabel("-")
        self.price_label.setStyleSheet("color: white;")
        right_layout.addWidget(self.price_label)

        date_row = QHBoxLayout()
        date_label = QLabel("Dátum:")
        date_label.setStyleSheet("color: white;")
        date_row.addWidget(date_label)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMinimumDate(QDate.currentDate())
        date_row.addWidget(self.date_edit)

        right_layout.addLayout(date_row)

        self.check_button = QPushButton("Foglaltság ellenőrzése")
        self.check_button.clicked.connect(self.refresh_availability)
        right_layout.addWidget(self.check_button)

        self.availability_morning = QLabel("Délelőtt: -")
        self.availability_afternoon = QLabel("Délután: -")
        self.availability_full_day = QLabel("Egész nap: -")

        for label in [
            self.availability_morning,
            self.availability_afternoon,
            self.availability_full_day,
        ]:
            label.setStyleSheet("font-size: 14px; color: white;")
            right_layout.addWidget(label)

        self.period_combo = QComboBox()
        self.period_combo.addItems(["morning", "afternoon", "full_day"])
        right_layout.addWidget(self.period_combo)

        self.book_button = QPushButton("Foglalás")
        self.book_button.clicked.connect(self.book_selected_trailer)
        right_layout.addWidget(self.book_button)

        self.login_hint = QLabel("")
        self.login_hint.setWordWrap(True)
        self.login_hint.setStyleSheet("color: #fbbf24;")
        right_layout.addWidget(self.login_hint)

        right_layout.addStretch()

        self.load_trailers()
        self.refresh_auth_state()

    def load_trailers(self):
        self.trailers = self.viewmodel.get_all_trailers()
        self.list_widget.clear()

        for trailer in self.trailers:
            text = (
                f"{trailer.name} | Délelőtt: {trailer.price_morning} Ft | "
                f"Délután: {trailer.price_afternoon} Ft | Egész nap: {trailer.price_full_day} Ft"
            )
            self.list_widget.addItem(QListWidgetItem(text))

        if self.trailers:
            self.list_widget.setCurrentRow(0)
        else:
            self.name_label.setText("Nincs elérhető utánfutó")
            self.description_label.setText("A listában jelenleg nincs aktív utánfutó.")
            self.price_label.setText("")
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("Nincs kép")
            self.clear_availability_labels()

    def refresh(self):
        self.load_trailers()
        self.refresh_auth_state()

    def refresh_auth_state(self):
        is_logged_in = SessionManager.instance().is_authenticated()
        self.book_button.setVisible(is_logged_in)
        self.period_combo.setVisible(is_logged_in)

        if is_logged_in:
            self.login_hint.setText("")
        else:
            self.login_hint.setText("Foglalni csak bejelentkezés után lehet.")

    def on_trailer_selected(self, row: int):
        if row < 0 or row >= len(self.trailers):
            return

        trailer = self.trailers[row]
        self.name_label.setText(trailer.name)
        self.description_label.setText(trailer.description or "Nincs leírás.")
        self.price_label.setText(
            f"Délelőtt: {trailer.price_morning} Ft | "
            f"Délután: {trailer.price_afternoon} Ft | "
            f"Egész nap: {trailer.price_full_day} Ft | "
            f"Kaució: {trailer.deposit} Ft"
        )

        self.load_trailer_image(getattr(trailer, "image_path", None))
        self.refresh_availability()

    def load_trailer_image(self, image_path):
        if not image_path:
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("Nincs kép")
            return

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("Kép nem található")
            return

        scaled = pixmap.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)
        self.image_label.setText("")

    def get_selected_trailer(self):
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.trailers):
            return None
        return self.trailers[row]

    def get_selected_booking_date(self) -> date:
        selected = self.date_edit.date()
        return date(selected.year(), selected.month(), selected.day())

    def clear_availability_labels(self):
        self.availability_morning.setText("Délelőtt: -")
        self.availability_afternoon.setText("Délután: -")
        self.availability_full_day.setText("Egész nap: -")

    def refresh_availability(self):
        trailer = self.get_selected_trailer()
        if trailer is None:
            self.clear_availability_labels()
            return

        booking_date = self.get_selected_booking_date()
        availability = get_availability_for_trailer_and_date(trailer.id, booking_date)

        self.availability_morning.setText(
            f"Délelőtt: {'Szabad' if availability['morning'] else 'Foglalt'}"
        )
        self.availability_afternoon.setText(
            f"Délután: {'Szabad' if availability['afternoon'] else 'Foglalt'}"
        )
        self.availability_full_day.setText(
            f"Egész nap: {'Szabad' if availability['full_day'] else 'Foglalt'}"
        )

    def book_selected_trailer(self):
        trailer = self.get_selected_trailer()
        if trailer is None:
            QMessageBox.warning(self, "Hiba", "Először válassz utánfutót.")
            return

        user = SessionManager.instance().get_user()
        if not user:
            QMessageBox.warning(self, "Hiba", "Foglaláshoz be kell jelentkezni.")
            return

        booking_date = self.get_selected_booking_date()
        period = self.period_combo.currentText()

        try:
            create_booking(user.id, trailer.id, booking_date, period)
            QMessageBox.information(self, "Siker", "A foglalás sikeresen létrejött.")
            self.refresh_availability()
        except ValueError as exc:
            QMessageBox.warning(self, "Hiba", str(exc))
        except Exception as exc:
            QMessageBox.critical(self, "Hiba", f"Váratlan hiba történt: {exc}")