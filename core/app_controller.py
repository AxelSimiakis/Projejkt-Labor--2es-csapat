"""
core/app_controller.py
----------------------


Feladata:
- Jelek (signals) bekötése: View -> Controller
- Navigáció kezelése
- Guard logika (mely oldalak publikusak és melyek védettek)
- Login és Register folyamat kezelése
- Üzenetek / state frissítés a view-kban

"""

from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from services.auth_service import AuthService
from services.register_service import RegisterService


class AppController:
    """
    Központi controller.

    Az alkalmazás állapota (egyszerűsítve):
    - is_authenticated: bool (belépett-e)
    - pending_route: hova akart a user menni (login után ide dobjuk)
    """

    # Publikus route-ok: ezek belépés nélkül is elérhetők
    PUBLIC_ROUTES = {"rolunk", "regisztracio", "belepes"}

    def __init__(self, window) -> None:
        self.window = window

        # Service réteg: később a backendes ezeket kötheti API-hoz
        self.auth_service = AuthService()
        self.register_service = RegisterService()

        # Egyszerű auth state
        self.is_authenticated: bool = False

        # Ha user védett menüpontra kattint belépés előtt,
        # ide mentjük és login után ide navigálunk.
        self.pending_route: str = "kereses"

        # Jelek bekötése (UI -> Controller)
        self._wire_signals()

        # Kezdő UI állapot
        self.window.login_view.set_active_nav("belepes")
        self.window.login_view.set_info_text_for_route("belepes")

        self.window.register_view.set_active_nav("regisztracio")

    def _wire_signals(self) -> None:
        """
        Összeköti a View-k signal-jeit a controller metódusaival.
        """
        # ----- LoginView -----
        lv = self.window.login_view
        lv.login_requested.connect(self.on_login_requested)
        lv.google_login_requested.connect(self.on_google_login_requested)

        # Top menü gombok route-ot küldenek (rolunk/szures/kereses)
        lv.nav_clicked.connect(self.on_nav_clicked)

        # LoginView-ben külön signal a regisztráció/belépés menüpontra
        lv.register_clicked.connect(lambda: self.on_nav_clicked("regisztracio"))
        lv.enter_clicked.connect(lambda: self.on_nav_clicked("belepes"))

        # ----- RegisterView -----
        rv = self.window.register_view
        rv.register_requested.connect(self.on_register_requested)
        rv.google_register_requested.connect(self.on_google_register_requested)

        rv.nav_clicked.connect(self.on_nav_clicked)
        rv.register_menu_clicked.connect(lambda: self.on_nav_clicked("regisztracio"))
        rv.login_menu_clicked.connect(lambda: self.on_nav_clicked("belepes"))

    # ==========================================================
    # NAV / ROUTING + GUARD
    # ==========================================================
    def on_nav_clicked(self, route: str) -> None:
        """
        Menüpontra kattintás kezelése.

        Guard logika:
        - PUBLIC_ROUTES: belépés nélkül is mehet
        - egyéb route-ok: csak belépés után
        """
        self.pending_route = route

        # Aktív menü "bekarikázása" mindkét view-n
        self.window.login_view.set_active_nav(route)
        self.window.register_view.set_active_nav(route)

        # Login oldali info szöveg route szerint változik
        self.window.login_view.set_info_text_for_route(route)

        # 1) Publikus oldalak: azonnal megjelenhetnek
        if route in self.PUBLIC_ROUTES:
            self.window.show_route(route)
            return

        # 2) Védett oldalak: ha nincs login, marad a belépés oldal
        if not self.is_authenticated:
            self.window.show_route("belepes")
            return

        # 3) Belépve: mehet a kért oldal
        self.window.show_route(route)

    # ==========================================================
    # LOGIN
    # ==========================================================
    def on_login_requested(self, email: str, password: str) -> None:
        """
        Normál belépés (email/jelszó).
        A View jelzi, a Controller a service-en keresztül ellenőriz.
        """
        self.window.login_view.set_busy(True)
        try:
            result = self.auth_service.authenticate(email, password)

            # UI státusz üzenet
            self.window.login_view.set_status(result.message, ok=result.success)

            if result.success:
                self.is_authenticated = True

                # Rövid popup visszajelzés
                QMessageBox.information(self.window, "Siker", "Sikeres bejelentkezés!")

                # Login után arra a route-ra dobjuk, amit a user előtte kért
                # (ha ez publikus route volt, akkor is működik)
                self.window.show_route(self.pending_route)
        finally:
            self.window.login_view.set_busy(False)

    def on_google_login_requested(self) -> None:
        """
        Google belépés (stub).
        Később OAuth flow ide kerülhet.
        """
        self.window.login_view.set_busy(True)
        try:
            result = self.auth_service.authenticate_with_google()
            self.window.login_view.set_status(result.message, ok=result.success)

            if result.success:
                self.is_authenticated = True
                QMessageBox.information(self.window, "Siker", "Sikeres Google belépés!")
                self.window.show_route(self.pending_route)
        finally:
            self.window.login_view.set_busy(False)

    # ==========================================================
    # REGISTER
    # ==========================================================
    def on_register_requested(self, data) -> None:
        """
        Regisztráció gomb megnyomása.
        A data egy RegisterData objektum (ui/register_view.py).
        """
        self.window.register_view.set_busy(True)
        try:
            result = self.register_service.register(data)
            self.window.register_view.set_status(result.message, ok=result.success)

            if result.success:
                QMessageBox.information(self.window, "Siker", "Sikeres regisztráció!")

                # Regisztráció után tipikusan belépésre irányítunk
                self.window.login_view.set_active_nav("belepes")
                self.window.login_view.set_info_text_for_route("belepes")
                self.window.show_route("belepes")
        finally:
            self.window.register_view.set_busy(False)

    def on_google_register_requested(self) -> None:
        """
        Google regisztráció (stub).
        Később OAuth.
        """
        self.window.register_view.set_status("Google regisztráció (demo).", ok=True)