class SessionManager:

    _instance = None

    def __init__(self):
        self._user = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = SessionManager()
        return cls._instance

    # ===== LOGIN =====
    def login(self, user):
        self._user = user

    # ===== LOGOUT =====
    def logout(self):
        self._user = None

    # ===== AUTH CHECK =====
    def is_authenticated(self):
        return self._user is not None

    # ===== USER OBJECT =====
    def get_user(self):
        return self._user

    # ===== USER ID =====
    def get_user_id(self):
        if self._user:
            return self._user.id
        return None

    # ===== ROLE =====
    def get_role(self):
        if self._user:
            return self._user.role
        return None