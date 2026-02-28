from services.auth_service import AuthService

success, user = AuthService.login("admin@admin.hu", "admin123")

if success:
    print("Sikeres bejelentkezés!")
    print("Role:", user.role)
else:
    print("Hibás belépés")