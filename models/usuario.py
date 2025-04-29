import sirope
from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, nombre, email, contraseña_hash):
        self.nombre = nombre
        self.email = email
        self.contraseña_hash = contraseña_hash

    def get_id(self):
        return self.email
