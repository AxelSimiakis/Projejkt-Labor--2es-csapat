"""
ui/register_view.py
-------------------
Regisztráció képernyő a minta alapján.

Elv:
- A View csak UI + Signal-ek
- Regisztráció logika a Controllerben
- Backend hívás a service rétegben (RegisterService)

Signal-ek:
- register_requested(RegisterData)
- google_register_requested()
- nav_clicked(route)
- register_menu_clicked()
- login_menu_clicked()
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy
)


@dataclass(frozen=True)
class RegisterData:
    """
    A regisztrációhoz beküldött adatok DTO-ja.
    (DTO = Data Transfer Object)
    """
    last_name: str
    first_name: str
    phone: str
    country: str
    zip_code: str
    county: str
    city: str
    street: str
    house_number: str
    email: str
    password: str


class RegisterView(QWidget):
    register_requested = Signal(object)   # RegisterData
    google_register_requested = Signal()

    nav_clicked = Signal(str)
    register_menu_clicked = Signal()
    login_menu_clicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._build_ui()
        self._apply_styles()

        # Alapértelmezett aktív menü
        self.set_active_nav("regisztracio")

    def _pill_input(self, placeholder: str, *, password: bool = False) -> QLineEdit:
        """
        Egységes pill stílusú QLineEdit létrehozása.
        """
        inp = QLineEdit(self)
        inp.setObjectName("pillInput")
        inp.setPlaceholderText(placeholder)
        if password:
            inp.setEchoMode(QLineEdit.Password)
        return inp

    def _build_ui(self) -> None:
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

        self.btn_about = QPushButton("Rólunk", header)
        self.btn_filter = QPushButton("Szűrés", header)
        self.btn_search = QPushButton("Keresés", header)
        self.btn_register_menu = QPushButton("Regisztráció", header)
        self.btn_login_menu = QPushButton("Belépés", header)

        for b in (self.btn_about, self.btn_filter, self.btn_search, self.btn_register_menu, self.btn_login_menu):
            b.setCursor(Qt.PointingHandCursor)
            b.setFlat(True)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Egyenlő elosztás
        nav_row.addWidget(self.btn_about, 1)
        nav_row.addWidget(self.btn_filter, 1)
        nav_row.addWidget(self.btn_search, 1)
        nav_row.addWidget(self.btn_register_menu, 1)
        nav_row.addWidget(self.btn_login_menu, 1)

        header_layout.addWidget(title)
        header_layout.addLayout(nav_row)

        # ===== Content =====
        content = QFrame(self)
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 20, 0, 20)
        content_layout.setSpacing(0)

        panel = QFrame(content)
        panel.setObjectName("registerPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 25, 0, 25)
        panel_layout.setSpacing(16)

        panel_title = QLabel("REGISZTRÁCIÓ", panel)
        panel_title.setObjectName("panelTitle")
        panel_title.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        form_wrap = QFrame(panel)
        form = QVBoxLayout(form_wrap)
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(10)

        def add_row(label_text: str, placeholder: str, *, password: bool = False) -> QLineEdit:
            """
            Egy sor: label + pill input, középre rendezve.
            """
            row = QHBoxLayout()
            row.setSpacing(18)

            lbl = QLabel(label_text, form_wrap)
            lbl.setObjectName("fieldLabel")
            lbl.setMinimumWidth(160)

            inp = self._pill_input(placeholder, password=password)
            inp.setMinimumWidth(300)

            row.addStretch(1)
            row.addWidget(lbl)
            row.addWidget(inp)
            row.addStretch(1)

            form.addLayout(row)
            return inp

        # Személyes adatok
        self.inp_last_name = add_row("Vezetéknév:", "Vezetéknév...")
        self.inp_first_name = add_row("Keresztnév:", "Keresztnév...")
        self.inp_phone = add_row("Telefon:", "+(36)...")

        form.addSpacing(8)

        # Cím adatok
        self.inp_country = add_row("Ország:", "Országnév...")
        self.inp_zip = add_row("Irányítószám:", "Irányítószám")
        self.inp_county = add_row("Vármegye:", "Vármegye..")
        self.inp_city = add_row("Város:", "Város...")
        self.inp_street = add_row("Utca:", "Utca")
        self.inp_house = add_row("Házszám:", "Házszám")

        form.addSpacing(8)

        # Fiók adatok
        self.inp_email = add_row("Email:", "E-mail...")
        self.inp_password = add_row("Jelszó:", "Jelszó...", password=True)

        self.google_button = QPushButton("GOOGLE BELÉPÉS", panel)
        self.google_button.setObjectName("googleButton")
        self.google_button.setCursor(Qt.PointingHandCursor)

        self.register_button = QPushButton("REGISZTRÁCIÓ", panel)
        self.register_button.setObjectName("registerButton")
        self.register_button.setCursor(Qt.PointingHandCursor)

        self.status_label = QLabel("", panel)
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.status_label.setWordWrap(True)

        panel_layout.addWidget(panel_title)
        panel_layout.addWidget(form_wrap)
        panel_layout.addSpacing(6)
        panel_layout.addWidget(self.google_button, alignment=Qt.AlignHCenter)
        panel_layout.addSpacing(6)
        panel_layout.addWidget(self.register_button, alignment=Qt.AlignHCenter)
        panel_layout.addWidget(self.status_label)

        content_layout.addWidget(panel)

        root.addWidget(header)
        root.addWidget(content, 1)

        # ===== Signal-ek =====
        self.btn_about.clicked.connect(lambda: self.nav_clicked.emit("rolunk"))
        self.btn_filter.clicked.connect(lambda: self.nav_clicked.emit("szures"))
        self.btn_search.clicked.connect(lambda: self.nav_clicked.emit("kereses"))
        self.btn_register_menu.clicked.connect(self.register_menu_clicked.emit)
        self.btn_login_menu.clicked.connect(self.login_menu_clicked.emit)

        self.google_button.clicked.connect(self.google_register_requested.emit)
        self.register_button.clicked.connect(self._emit_register)

        # Enter jelszó mezőn -> regisztráció
        self.inp_password.returnPressed.connect(self._emit_register)

    def _emit_register(self) -> None:
        """
        Összegyűjti a form adatait és elküldi a Controllernek.
        """
        data = RegisterData(
            last_name=self.inp_last_name.text(),
            first_name=self.inp_first_name.text(),
            phone=self.inp_phone.text(),
            country=self.inp_country.text(),
            zip_code=self.inp_zip.text(),
            county=self.inp_county.text(),
            city=self.inp_city.text(),
            street=self.inp_street.text(),
            house_number=self.inp_house.text(),
            email=self.inp_email.text(),
            password=self.inp_password.text(),
        )
        self.register_requested.emit(data)

    # ===== Controller API =====
    def set_status(self, text: str, *, ok: bool) -> None:
        self.status_label.setText(text)
        self.status_label.setProperty("ok", ok)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def set_busy(self, busy: bool) -> None:
        self.register_button.setEnabled(not busy)
        self.google_button.setEnabled(not busy)

    def set_active_nav(self, key: str) -> None:
        buttons = {
            "rolunk": self.btn_about,
            "szures": self.btn_filter,
            "kereses": self.btn_search,
            "regisztracio": self.btn_register_menu,
            "belepes": self.btn_login_menu,
        }
        for k, btn in buttons.items():
            btn.setProperty("active", k == key)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _apply_styles(self) -> None:
        self.setStyleSheet("""
            QWidget { font-family: "Times New Roman"; }

            #header { background: #00b050; }
            #brandTitle { color: white; font-size: 22px; font-weight: 700; padding-top: 6px; }

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

            #registerPanel { background: #00b050; }
            #panelTitle { color: white; font-size: 22px; font-weight: 800; letter-spacing: 1px; }

            #fieldLabel { color: white; font-size: 16px; font-weight: 600; }

            #pillInput {
                background: #5a7a2a;
                color: white;
                border: none;
                border-radius: 16px;
                padding: 6px 14px;
                font-size: 15px;
                min-height: 28px;
            }
            #pillInput::placeholder { color: rgba(255,255,255,0.75); }

            #googleButton {
                background: #5a7a2a;
                color: white;
                border: none;
                border-radius: 18px;
                padding: 10px 48px;
                font-size: 16px;
                font-weight: 700;
            }

            #registerButton {
                background: #ff0000;
                color: white;
                border: none;
                border-radius: 22px;
                padding: 12px 70px;
                font-size: 18px;
                font-weight: 800;
            }
            #registerButton:disabled { background: #cc5a5a; }

            #statusLabel { color: #eaffea; font-size: 14px; margin-top: 8px; }
            #statusLabel[ok="false"] { color: #ffe6e6; }
            #statusLabel[ok="true"] { color: #eaffea; }
        """)