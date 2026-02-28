"""
services/auth_service.py
------------------------
Autentikációs service (stub).


Most: demo belépés
- admin@potkocsipont.hu / 1234
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthResult:
    """Egységes eredmény objektum a belépéshez."""
    success: bool
    message: str


class AuthService:
    """
    Backend-hez csatlakozó autentikációs réteg (stub).
    """

    def authenticate(self, email: str, password: str) -> AuthResult:
        """
        Email/jelszó ellenőrzés (demo).
        """
        email = (email or "").strip()

        if not email or not password:
            return AuthResult(False, "Kérlek add meg az email címet és a jelszót!")

        # Demo felhasználó (később backendből jön)
        if email.lower() == "admin@potkocsipont.hu" and password == "1234":
            return AuthResult(True, "Sikeres belépés!")

        return AuthResult(False, "Hibás email vagy jelszó!")

    def authenticate_with_google(self) -> AuthResult:
        """
        Google belépés stub.
        Ide jöhet OAuth flow (webview/redirect/token).
        """
        return AuthResult(True, "Google belépés (demo) sikeres!")