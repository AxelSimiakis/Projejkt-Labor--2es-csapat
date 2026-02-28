class SessionManager:
    _instance = None

    def __init__(self):
        self.current_user = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = SessionManager()
        return cls._instance

    def login(self, user):
        self.current_user = user

    def logout(self):
        self.current_user = None

    def is_authenticated(self):
        return self.current_user is not None

    def get_role(self):
        if self.current_user:
            return self.current_user.role
        return None