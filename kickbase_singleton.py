# kickbase_singleton.py
from kickbase_api.kickbase import Kickbase
from kickbase_api.exceptions import KickbaseLoginException


class KickbaseSingleton(Kickbase):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.kb = None
            cls._instance.user = None
            cls._instance.leagues = None
        return cls._instance

    def login(self, email, password):
        try:
            self.kb = Kickbase()
            self.user, self.leagues = self.kb.login(email, password)
            return True
        except KickbaseLoginException:
            return False


kickbase_singleton = KickbaseSingleton()
