from datetime import date
import calendar

from PySide6.QtCore import QDate, Qt, Signal, QRect
from PySide6.QtGui import QPixmap, QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFrame,
    QScrollArea,
    QGridLayout,
    QCalendarWidget,
)

from core.session_manager import SessionManager
from core.toast import Toast
from services.booking_service import (
    create_booking,
    get_availability_for_trailer_and_date,
    get_availability_map_for_period,
)
from services.favorite_service import (
    get_favorite_trailer_ids,
    toggle_favorite,
)
from services.cart_service import add_to_cart
from viewmodels.trailer_list_vm import TrailerListViewModel


class AvailabilityCalendar(QCalendarWidget):
    dayClicked = Signal(QDate)
    pageChangedManually = Signal(int, int)

    def __init__(self):
        super().__init__()
        self.availability_map = {}

        self.setGridVisible(True)
        self.clicked.connect(self.dayClicked.emit)
        self.currentPageChanged.connect(self._emit_page_changed)

        self.setStyleSheet("""
            QCalendarWidget QWidget {
                alternate-background-color: #111827;
                background-color: #111827;
                color: white;
                font-size: 11px;
            }
            QCalendarWidget QToolButton {
                color: white;
                font-weight: bold;
                background: transparent;
                margin: 2px;
                padding: 4px;
            }
            QCalendarWidget QMenu {
                background-color: #1f2937;
                color: white;
            }
            QCalendarWidget QSpinBox {
                color: white;
                background-color: #1f2937;
                selection-background-color: #16a34a;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: white;
                background-color: #111827;
                selection-background-color: transparent;
                selection-color: white;
                font-size: 11px;
            }
        """)

    def _emit_page_changed(self, year, month):
        self.pageChangedManually.emit(year, month)

    def set_availability_map(self, availability_map: dict):
        self.availability_map = availability_map
        self.updateCells()

    def paintCell(self, painter: QPainter, rect: QRect, qdate: QDate):
        py_date = date(qdate.year(), qdate.month(), qdate.day())
        today = date.today()
        state = self.availability_map.get(py_date, "free")

        painter.save()

        if py_date <= today:
            painter.fillRect(rect.adjusted(2, 2, -2, -2), QColor("#6b7280"))
        else:
                if state == "full":
                    painter.fillRect(rect.adjusted(2, 2, -2, -2), QColor("#dc2626"))
                elif state == "partial":
                    painter.fillRect(rect.adjusted(2, 2, -2, -2), QColor("#f59e0b"))
                else:
                    painter.fillRect(rect.adjusted(2, 2, -2, -2), QColor("#16a34a"))
            
        if qdate == self.selectedDate():
            pen = QPen(QColor("#ffffff"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(rect.adjusted(1, 1, -2, -2))

        painter.setPen(QColor("white"))
        painter.drawText(rect, Qt.AlignCenter, str(qdate.day()))
        painter.restore()


class TrailerCard(QFrame):
    clicked = Signal(object)

    def __init__(self, trailer, is_favorite=False, favorite_callback=None):
        super().__init__()
        self.trailer = trailer
        self.favorite_callback = favorite_callback
        self._is_favorite = is_favorite

        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("trailerCard")
        self.setStyleSheet("""
            QFrame#trailerCard {
                background-color: #1f2937;
                border: 1px solid #374151;
                border-radius: 14px;
            }
            QFrame#trailerCard:hover {
                border: 1px solid #16a34a;
                background-color: #243042;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.image_label = QLabel()
        self.image_label.setFixedHeight(140)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #111827;
            border-radius: 10px;
            color: #9ca3af;
        """)

        pixmap = QPixmap(getattr(trailer, "image_path", "") or "")
        if not pixmap.isNull():
            self.image_label.setPixmap(
                pixmap.scaled(
                    260,
                    140,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
            )
        else:
            self.image_label.setText("Nincs kép")

        self.name_label = QLabel(trailer.name)
        self.name_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
            background: transparent;
        """)

        self.desc_label = QLabel((trailer.description or "Nincs leírás.")[:70])
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("""
            color: #d1d5db;
            font-size: 12px;
            background: transparent;
        """)

        self.price_label = QLabel(
            f"Délelőtt: {trailer.price_morning} Ft\n"
            f"Délután: {trailer.price_afternoon} Ft\n"
            f"Egész nap: {trailer.price_full_day} Ft"
        )
        self.price_label.setStyleSheet("""
            color: #f3f4f6;
            font-size: 12px;
            background: transparent;
        """)

        bottom_row = QHBoxLayout()
        bottom_row.addStretch()

        self.favorite_button = QPushButton()
        self.favorite_button.setFixedSize(34, 34)
        self.favorite_button.setCursor(Qt.PointingHandCursor)
        self.favorite_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #fbbf24;
                font-size: 22px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(251, 191, 36, 0.08);
                border-radius: 17px;
            }
        """)
        self.favorite_button.clicked.connect(self.handle_favorite_clicked)
        bottom_row.addWidget(self.favorite_button)

        self.update_favorite_icon()

        layout.addWidget(self.image_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.desc_label)
        layout.addWidget(self.price_label)
        layout.addLayout(bottom_row)

    def set_favorite(self, is_favorite: bool):
        self._is_favorite = is_favorite
        self.update_favorite_icon()

    def update_favorite_icon(self):
        self.favorite_button.setText("★" if self._is_favorite else "☆")

    def handle_favorite_clicked(self):
        if self.favorite_callback:
            self.favorite_callback(self.trailer)

    def mousePressEvent(self, event):
        child = self.childAt(event.position().toPoint()) if hasattr(event, "position") else self.childAt(event.pos())
        if child == self.favorite_button:
            super().mousePressEvent(event)
            return

        self.clicked.emit(self.trailer)
        super().mousePressEvent(event)


class TrailerListView(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.viewmodel = TrailerListViewModel()
        self.trailers = []
        self.selected_trailer = None
        self.favorite_ids = set()

        self.setWindowTitle("Elérhető utánfutók")

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(20)

        left_wrapper = QFrame()
        left_layout = QVBoxLayout(left_wrapper)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        left_title = QLabel("Elérhető utánfutók")
        left_title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        left_layout.addWidget(left_title)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(16)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll.setWidget(self.cards_container)
        left_layout.addWidget(self.scroll)
        root.addWidget(left_wrapper, 3)

        self.right_scroll = QScrollArea()
        self.right_scroll.setWidgetResizable(True)
        self.right_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.right_panel = QFrame()
        self.right_panel.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 16px;
                color: white;
            }
        """)
        self.right_panel.setMinimumWidth(430)

        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(18, 18, 18, 18)
        right_layout.setSpacing(8)

        self.image_label = QLabel("Válassz egy utánfutót")
        self.image_label.setFixedHeight(220)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #111827;
            border: 1px solid #374151;
            border-radius: 12px;
            color: #9ca3af;
            font-size: 16px;
        """)
        right_layout.addWidget(self.image_label)

        self.name_label = QLabel("Nincs kiválasztott utánfutó")
        self.name_label.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        right_layout.addWidget(self.name_label)

        self.description_label = QLabel("Kattints a bal oldali csempék egyikére.")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #d1d5db; font-size: 14px;")
        right_layout.addWidget(self.description_label)

        self.price_label = QLabel("-")
        self.price_label.setStyleSheet("color: white; font-size: 14px;")
        right_layout.addWidget(self.price_label)

        legend = QLabel("Jelmagyarázat: zöld = szabad, sárga = részben foglalt, piros = teljesen foglalt")
        legend.setWordWrap(True)
        legend.setStyleSheet("color: #d1d5db; font-size: 12px;")
        right_layout.addWidget(legend)

        self.calendar = AvailabilityCalendar()
        self.calendar.setFixedHeight(280)
        self.calendar.dayClicked.connect(self.on_calendar_day_selected)
        self.calendar.pageChangedManually.connect(self.refresh_calendar_month)
        right_layout.addWidget(self.calendar)

        self.selected_date_label = QLabel("Kiválasztott dátum: -")
        self.selected_date_label.setStyleSheet("color: white; font-size: 14px;")
        right_layout.addWidget(self.selected_date_label)

        self.availability_morning = QLabel("Délelőtt: -")
        self.availability_afternoon = QLabel("Délután: -")
        self.availability_full_day = QLabel("Egész nap: -")

        for label in [self.availability_morning, self.availability_afternoon, self.availability_full_day]:
            label.setStyleSheet("color: white; font-size: 14px; background: transparent;")
            right_layout.addWidget(label)

        self.period_combo = QComboBox()
        self.period_combo.addItem("Délelőtt", "morning")
        self.period_combo.addItem("Délután", "afternoon")
        self.period_combo.addItem("Egész nap", "full_day")
        self.period_combo.setStyleSheet("""
            QComboBox {
                background-color: #111827;
                color: white;
                padding: 8px;
                border-radius: 8px;
                border: 1px solid #374151;
            }
        """)
        right_layout.addWidget(self.period_combo)

        actions_row = QHBoxLayout()

        self.favorite_action_button = QPushButton("☆ Kedvenc")
        self.favorite_action_button.clicked.connect(self.toggle_selected_favorite)
        self.favorite_action_button.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: #fbbf24;
                padding: 10px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        actions_row.addWidget(self.favorite_action_button, 1)

        self.book_button = QPushButton("Foglalás")
        self.book_button.clicked.connect(self.book_selected_trailer)
        self.book_button.setStyleSheet("""
            QPushButton {
                background-color: #16a34a;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #15803d;
            }
        """)
        actions_row.addWidget(self.book_button, 2)

        right_layout.addLayout(actions_row)

        self.login_hint = QLabel("")
        self.login_hint.setWordWrap(True)
        self.login_hint.setStyleSheet("color: #fbbf24;")
        right_layout.addWidget(self.login_hint)

        right_layout.addStretch()

        self.right_scroll.setWidget(self.right_panel)
        root.addWidget(self.right_scroll, 2)

        self.load_trailers()
        self.refresh_auth_state()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def load_favorites(self):
        user = SessionManager.instance().get_user()
        self.favorite_ids = get_favorite_trailer_ids(user.id) if user else set()

    def load_trailers(self):
        self.load_favorites()
        self.trailers = self.viewmodel.get_all_trailers()
        self.clear_layout(self.cards_layout)

        columns = 2
        row = 0
        col = 0

        for trailer in self.trailers:
            card = TrailerCard(
                trailer,
                is_favorite=trailer.id in self.favorite_ids,
                favorite_callback=self.toggle_trailer_favorite
            )
            card.clicked.connect(self.select_trailer)
            self.cards_layout.addWidget(card, row, col)

            col += 1
            if col >= columns:
                col = 0
                row += 1

        if self.trailers:
            current_id = self.selected_trailer.id if self.selected_trailer else None
            selected = next((t for t in self.trailers if t.id == current_id), self.trailers[0])
            self.select_trailer(selected)
        else:
            self.selected_trailer = None
            self.name_label.setText("Nincs elérhető utánfutó")
            self.description_label.setText("A listában jelenleg nincs aktív utánfutó.")
            self.price_label.setText("-")
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("Nincs kép")
            self.selected_date_label.setText("Kiválasztott dátum: -")
            self.favorite_action_button.setText("☆ Kedvenc")
            self.clear_availability_labels()

    def refresh(self):
        self.load_trailers()
        self.refresh_auth_state()

    def refresh_auth_state(self):
        is_logged_in = SessionManager.instance().is_authenticated()
        self.book_button.setVisible(is_logged_in)
        self.period_combo.setVisible(is_logged_in)
        self.favorite_action_button.setVisible(is_logged_in)

        if is_logged_in:
            self.login_hint.setText("")
        else:
            self.login_hint.setText("Foglalni és kedvencekhez adni csak bejelentkezés után lehet.")

    def update_selected_favorite_button(self):
        if not self.selected_trailer:
            self.favorite_action_button.setText("☆ Kedvenc")
            return

        if self.selected_trailer.id in self.favorite_ids:
            self.favorite_action_button.setText("★ Kedvenc")
        else:
            self.favorite_action_button.setText("☆ Kedvenc")

    def select_trailer(self, trailer):
        self.selected_trailer = trailer
        self.name_label.setText(trailer.name)
        self.description_label.setText(trailer.description or "Nincs leírás.")
        self.price_label.setText(
            f"Délelőtt: {trailer.price_morning} Ft | "
            f"Délután: {trailer.price_afternoon} Ft | "
            f"Egész nap: {trailer.price_full_day} Ft | "
            f"Kaució: {trailer.deposit} Ft"
        )

        self.load_trailer_image(getattr(trailer, "image_path", None))
        self.update_selected_favorite_button()

        selected_qdate = self.calendar.selectedDate()
        self.selected_date_label.setText(
            f"Kiválasztott dátum: {selected_qdate.toString('yyyy.MM.dd.')}"
        )

        self.refresh_calendar_month(selected_qdate.year(), selected_qdate.month())
        self.refresh_day_availability()

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

    def on_calendar_day_selected(self, qdate: QDate):
        self.selected_date_label.setText(f"Kiválasztott dátum: {qdate.toString('yyyy.MM.dd.')}")
        self.refresh_day_availability()

    def get_selected_booking_date(self) -> date:
        qdate = self.calendar.selectedDate()
        return date(qdate.year(), qdate.month(), qdate.day())

    def refresh_calendar_month(self, year: int, month: int):
        if not self.selected_trailer:
            return

        first_day = date(year, month, 1)
        last_day_num = calendar.monthrange(year, month)[1]
        last_day = date(year, month, last_day_num)

        availability_map = get_availability_map_for_period(
            self.selected_trailer.id,
            first_day,
            last_day
        )
        self.calendar.set_availability_map(availability_map)
        self.refresh_day_availability()

    def clear_availability_labels(self):
        self.availability_morning.setText("Délelőtt: -")
        self.availability_afternoon.setText("Délután: -")
        self.availability_full_day.setText("Egész nap: -")

    def refresh_day_availability(self):
        if not self.selected_trailer:
            self.clear_availability_labels()
            return

        booking_date = self.get_selected_booking_date()
        availability = get_availability_for_trailer_and_date(self.selected_trailer.id, booking_date)

        self.availability_morning.setText(
            f"Délelőtt: {'Szabad' if availability['morning'] else 'Foglalt'}"
        )
        self.availability_afternoon.setText(
            f"Délután: {'Szabad' if availability['afternoon'] else 'Foglalt'}"
        )
        self.availability_full_day.setText(
            f"Egész nap: {'Szabad' if availability['full_day'] else 'Foglalt'}"
        )

    def toggle_trailer_favorite(self, trailer):
        user = SessionManager.instance().get_user()
        if not user:
            Toast(self.main_window or self, "Kedvencekhez adáshoz be kell jelentkezni.", success=False).show_toast()
            return

        try:
            now_favorite = toggle_favorite(user.id, trailer.id)

            if now_favorite:
                self.favorite_ids.add(trailer.id)
                Toast(self.main_window or self, "Utánfutó hozzáadva a kedvencekhez", success=True).show_toast()
            else:
                self.favorite_ids.discard(trailer.id)
                Toast(self.main_window or self, "Utánfutó eltávolítva a kedvencekből", success=False).show_toast()

            if self.selected_trailer and self.selected_trailer.id == trailer.id:
                self.update_selected_favorite_button()

            self.load_trailers()

            if hasattr(self.main_window, "favorite_page"):
                self.main_window.favorite_page.load_data()

        except Exception as exc:
            Toast(self.main_window or self, f"Hiba történt: {exc}", success=False).show_toast()

    def toggle_selected_favorite(self):
        if not self.selected_trailer:
            Toast(self.main_window or self, "Először válassz utánfutót.", success=False).show_toast()
            return

        self.toggle_trailer_favorite(self.selected_trailer)

    def book_selected_trailer(self):
        if self.selected_trailer is None:
            Toast(self.main_window or self, "Először válassz utánfutót.", success=False).show_toast()
            return

        user = SessionManager.instance().get_user()
        if not user:
            Toast(self.main_window or self, "Foglaláshoz be kell jelentkezni.", success=False).show_toast()
            return

        booking_date = self.get_selected_booking_date()
        period = self.period_combo.currentData()

        today = date.today()

        if user.role == "user":
            diff = (booking_date - today).days

            if booking_date <= today:
                Toast(
                    self.main_window or self,
                    "Múltbeli dátum nem választható!",
                    success=False
                ).show_toast()
                return

            if diff <= 2:
                Toast(
                    self.main_window or self,
                    "Csak a helyszínen személyesen, telefonon érdeklődjön!",
                    success=False
                ).show_toast()
                return

        try:
            add_to_cart(user.id, self.selected_trailer.id, booking_date, period)

            Toast(
                self.main_window or self,
                f"A tétel bekerült a kosárba: {self.selected_trailer.name} - {booking_date.strftime('%Y.%m.%d.')}",
                success=True
            ).show_toast()

            if hasattr(self.main_window, "cart_page"):
                self.main_window.cart_page.load_data()

        except ValueError as exc:
            Toast(self.main_window or self, str(exc), success=False).show_toast()

        except Exception as exc:
            Toast(self.main_window or self, f"Váratlan hiba történt: {exc}", success=False).show_toast()