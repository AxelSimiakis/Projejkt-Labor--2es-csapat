"""
services/register_service.py
----------------------------
Regisztrációs service (stub).

Cél:
- A regisztrációs logika 

Most: minimál validáció + demo siker.
"""

from __future__ import annotations

from dataclasses import dataclass
from ui.register_view import RegisterData


@dataclass(frozen=True)
class RegisterResult:
    """Egységes eredmény objektum a regisztrációhoz."""
    success: bool
    message: str


class RegisterService:
    """
    Regisztrációs réteg (stub).
    """

    def register(self, data: RegisterData) -> RegisterResult:
        """
        Demo regisztráció:
        - pár alap mezőt ellenőrzünk
        - mindig 'siker' ha rendben
        """
        if not data.last_name.strip() or not data.first_name.strip():
            return RegisterResult(False, "A vezetéknév és keresztnév megadása kötelező.")

        if "@" not in data.email:
            return RegisterResult(False, "Adj meg érvényes email címet.")

        if len(data.password) < 4:
            return RegisterResult(False, "A jelszó legalább 4 karakter legyen (demo).")

        # Később: API request -> backend -> válasz feldolgozás
        return RegisterResult(True, "Sikeres regisztráció! Most már beléphetsz.")