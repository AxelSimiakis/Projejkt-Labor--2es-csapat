"""
ui/login_view.py
----------------
Login képernyő + felső navbar.

Elv:
- A View csak UI-t rajzol és Signal-eket küld.
- Üzleti logika (auth, route guard, stb.) NEM itt van, hanem Controllerben.

Signal-ek:
- login_requested(email, password)
- google_login_requested()
- nav_clicked(route)
- register_clicked()
- enter_clicked()
"""

from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy
)


class NavButton(QPushButton):
    """
    Navbar gomb alap osztály.
    active property-t használunk (QSS-ben bekarikázáshoz).
    """

    def __init__(self, text: str, *, active: bool = False, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFlat(True)
        self.setProperty("active", active)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class LoginView(QWidget):
    # View -> Controller kommunikáció
    login_requested = Signal(str, str)     # email, password
    google_login_requested = Signal()
    nav_clicked = Signal(str)             # "rolunk" | "szures" | "kereses"
    register_clicked = Signal()
    enter_clicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._build_ui()
        self._apply_styles()

        # Alapértelmezett aktív menü
        self.set_active_nav("belepes")

    def _build_ui(self) -> None:
        """
        UI felépítése: header + content.
        """
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ===== Header / Navbar =====
        header = QFrame(self)
        header.setObjectName("header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 10, 0, 10)
        header_layout.setSpacing(8)

        title = QLabel("PótkocsiPont", header)
        title.setObjectName("brandTitle")
        title.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        nav_row = QHBoxLayout()
        nav_row.setContentsMargins(30, 0, 30, 0)
        nav_row.setSpacing(18)

        self.btn_about = NavButton("Rólunk")
        self.btn_filter = NavButton("Szűrés")
        self.btn_search = NavButton("Keresés")
        self.btn_register = NavButton("Regisztráció")
        self.btn_login_menu = NavButton("Belépés")

        # Egyenlő elosztás
        nav_row.addWidget(self.btn_about, 1)
        nav_row.addWidget(self.btn_filter, 1)
        nav_row.addWidget(self.btn_search, 1)
        nav_row.addWidget(self.btn_register, 1)
        nav_row.addWidget(self.btn_login_menu, 1)

        header_layout.addWidget(title)
        header_layout.addLayout(nav_row)

        # ===== Content =====
        content = QFrame(self)
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 25, 0, 25)
        content_layout.setSpacing(18)

        # Információs sor (route alapján változik)
        self.info_label = QLabel("Foglaláshoz, regisztráljon illetve lépjen be!", content)
        self.info_label.setObjectName("infoText")
        self.info_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Login card
        card = QFrame(content)
        card.setObjectName("loginCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 28, 35, 28)
        card_layout.setSpacing(16)

        card_title = QLabel("BELÉPÉS", card)
        card_title.setObjectName("cardTitle")
        card_title.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Email sor
        email_row = QHBoxLayout()
        email_row.setSpacing(12)
        email_label = QLabel("Email:", card)
        email_label.setObjectName("fieldLabel")
        self.email_input = QLineEdit(card)
        self.email_input.setObjectName("pillInput")
        self.email_input.setPlaceholderText("pl. admin@potkocsipont.hu")
        email_row.addWidget(email_label)
        email_row.addWidget(self.email_input, 1)

        # Jelszó sor
        pass_row = QHBoxLayout()
        pass_row.setSpacing(12)
        pass_label = QLabel("Jelszó:", card)
        pass_label.setObjectName("fieldLabel")
        self.password_input = QLineEdit(card)
        self.password_input.setObjectName("pillInput")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("••••")
        pass_row.addWidget(pass_label)
        pass_row.addWidget(self.password_input, 1)

        # Google belépés (stub)
        self.google_button = QPushButton("GOOGLE BELÉPÉS", card)
        self.google_button.setObjectName("googleButton")
        self.google_button.setCursor(Qt.PointingHandCursor)

        # Belépés gomb
        self.login_button = QPushButton("BELÉPÉS", card)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setObjectName("loginButton")

        # Státusz label (hibák/siker)
        self.status_label = QLabel("", card)
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.status_label.setWordWrap(True)

        # Card layout
        card_layout.addWidget(card_title)
        card_layout.addLayout(email_row)
        card_layout.addLayout(pass_row)
        card_layout.addWidget(self.google_button, alignment=Qt.AlignHCenter)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.login_button)
        card_layout.addWidget(self.status_label)

        content_layout.addWidget(self.info_label)
        content_layout.addWidget(card, alignment=Qt.AlignHCenter)

        root.addWidget(header)
        root.addWidget(content, 1)

        # ===== Signal wiring (View -> Controller) =====
        # Gombok
        self.login_button.clicked.connect(self._emit_login)
        self.google_button.clicked.connect(self.google_login_requested.emit)

        # Navbar route-ok
        self.btn_about.clicked.connect(lambda: self.nav_clicked.emit("rolunk"))
        self.btn_filter.clicked.connect(lambda: self.nav_clicked.emit("szures"))
        self.btn_search.clicked.connect(lambda: self.nav_clicked.emit("kereses"))
        self.btn_register.clicked.connect(self.register_clicked.emit)
        self.btn_login_menu.clicked.connect(self.enter_clicked.emit)

        # Enter a mezőkben -> belépés
        self.email_input.returnPressed.connect(self._emit_login)
        self.password_input.returnPressed.connect(self._emit_login)

    def _emit_login(self) -> None:
        """
        Login kérés signal kibocsátása.
        """
        self.login_requested.emit(self.email_input.text(), self.password_input.text())

    # ====== Publikus API a Controller felé ======

    def set_status(self, text: str, *, ok: bool) -> None:
        """
        Állapot üzenet frissítése.
        ok=True/False property alapján
        """
        self.status_label.setText(text)
        self.status_label.setProperty("ok", ok)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def set_busy(self, busy: bool) -> None:
        """
        Terhelés/jelzés: gombok tiltása folyamat közben.
        """
        self.login_button.setEnabled(not busy)
        self.google_button.setEnabled(not busy)

    def set_active_nav(self, key: str) -> None:
        """
        Navbar aktív elem (bekarikázás) beállítása.
        key: 'rolunk' | 'szures' | 'kereses' | 'regisztracio' | 'belepes'
        """
        buttons = {
            "rolunk": self.btn_about,
            "szures": self.btn_filter,
            "kereses": self.btn_search,
            "regisztracio": self.btn_register,
            "belepes": self.btn_login_menu,
        }
        for k, btn in buttons.items():
            btn.setProperty("active", k == key)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def set_info_text_for_route(self, route: str) -> None:
        """
        A felső információs szöveg route alapján változik.
        """
        mapping = {
            "rolunk": "A Rólunk oldal megtekintéséhez regisztráljon vagy lépjen be!",
            "szures": "A szűréshez regisztráljon vagy lépjen be!",
            "kereses": "A kereséshez regisztráljon vagy lépjen be!",
            "regisztracio": "A regisztrációhoz kérlek töltsd ki az adatokat!",
            "belepes": "A belépéshez add meg az adataidat!",
        }
        self.info_label.setText(mapping.get(route, "A folytatáshoz regisztráljon vagy lépjen be!"))

    def _apply_styles(self) -> None:
        """
        QSS stílusok (demo).
        Később érdemes külön .qss fájlba tenni.
        """
        self.setStyleSheet("""
            QWidget { font-family: "Times New Roman"; }

            #header { background: #00b050; }
            #brandTitle { color: white; font-size: 22px; font-weight: 700; padding-top: 6px; }

            /* Navbar gombok */
            #header QPushButton {
                background: transparent;
                color: white;
                font-size: 18px;
                font-weight: 600;
                padding: 10px 0px;
                border: none;
            }
            #header QPushButton:hover { text-decoration: underline; }
            #header QPushButton[active="true"] {
                border: 2px solid white;
                border-radius: 18px;
                padding: 8px 0px;
            }

            #content { background: white; }
            #infoText { color: black; font-size: 18px; }

            #loginCard {
                background: #00b050;
                border-radius: 4px;
                min-width: 420px;
                max-width: 520px;
            }
            #cardTitle { color: white; font-size: 20px; font-weight: 800; letter-spacing: 1px; }

            #fieldLabel { color: white; font-size: 16px; min-width: 70px; }

            #pillInput {
                background: #5a7a2a;
                color: white;
                border: none;
                border-radius: 16px;
                padding: 6px 14px;
                font-size: 15px;
            }
            #pillInput::placeholder { color: rgba(255,255,255,0.75); }

            #googleButton {
                background: #5a7a2a;
                border: none;
                border-radius: 18px;
                padding: 10px 48px;
                font-size: 16px;
                font-weight: 700;
                color: white;
            }

            #loginButton {
                background: #ff0000;
                color: white;
                border-radius: 22px;
                padding: 12px 0px;
                font-size: 18px;
                font-weight: 800;
            }
            #loginButton:disabled { background: #cc5a5a; }

            #statusLabel { color: #eaffea; font-size: 14px; margin-top: 6px; }
            #statusLabel[ok="false"] { color: #ffe6e6; }
            #statusLabel[ok="true"] { color: #eaffea; }
        """)