import sirope
from flask_login import UserMixin
import uuid  # Para generar un ID único


class User(UserMixin):
    def __init__(self, id, name, username, email, password):
        self.id = id
        self.name = name
        self.username = username
        self.email = email
        self.password = password

    def get_id(self):
        return self.id
