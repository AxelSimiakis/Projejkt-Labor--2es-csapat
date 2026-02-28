"""
core/main_window.py
-------------------
A fő ablak (QMainWindow) felelőssége:

- Az alkalmazás oldalainak "tárolása" (QStackedWidget)
- A view-k példányosítása (LoginView, RegisterView, PlaceholderView-k)
- A navigációs route-ok hozzárendelése konkrét widgetekhez
- show_route() metódus biztosítása a controller számára

"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QScrollArea,
    QStackedWidget,
    QWidget,
    QVBoxLayout,
)

from ui.login_view import LoginView
from ui.register_view import RegisterView
from ui.placeholder_view import PlaceholderView

from core.app_controller import AppController


class MainWindow(QMainWindow):
    """
    Fő alkalmazás ablak.

    A QScrollArea wrapper azért van, hogy 900x900-as ablakban is
    a hosszú regisztrációs képernyő görgethető legyen.
    """

    def __init__(self) -> None:
        super().__init__()

        # Alap ablak beállítások
        self.setWindowTitle("PótkocsiPont")
        self.resize(1920, 1080)
        self.setMinimumSize(900, 900)

        # A QStackedWidget tartalmazza az "oldalakat"
        self.stack = QStackedWidget()

        # Scroll container:
        # - widgetResizable=True => a stack kitölti a rendelkezésre álló teret
        # - horizontal scroll off => UI-ban ne legyen vízszintes görgetés
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Wrapper widget a scroll area-hoz (a stack-et rakjuk bele)
        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(self.stack)

        self.scroll.setWidget(wrapper)
        self.setCentralWidget(self.scroll)

        # ========= View-k =========
        self.login_view = LoginView(self)
        self.register_view = RegisterView(self)

        # Placeholder oldalak (később lecserélhetők valós oldalakra)
        self.pages = {
            "belepes": self.login_view,
            "regisztracio": self.register_view,
            "rolunk": PlaceholderView("Rólunk", self),
            "szures": PlaceholderView("Szűrés", self),
            "kereses": PlaceholderView("Keresés", self),
        }

        # ========= Stack feltöltése =========
        # MINDEN route-hoz tartozó widgetet felveszünk a stack-be
        # (így könnyű a show_route-tal váltani)
        for key in ("belepes", "regisztracio", "rolunk", "szures", "kereses"):
            self.stack.addWidget(self.pages[key])

        # ========= Controller =========
        # A controller a window-ra hivatkozik, és kezeli:
        # - navigation
        # - auth/guard
        # - login/register folyamat
        self.controller = AppController(window=self)

        # Kezdő route
        self.show_route("belepes")

    def show_route(self, route: str) -> None:
        """
        Route váltás a stack-ben.

        Ha ismeretlen route jön, visszadob a belépés oldalra.
        """
        page = self.pages.get(route) or self.pages["belepes"]
        self.stack.setCurrentWidget(page)