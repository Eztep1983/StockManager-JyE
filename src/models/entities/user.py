from werkzeug.security import generate_password_hash, check_password_hash


class User:
    def __init__(self, id, identification, password, fullname="", active=True):
        self.id = id
        self.identification = identification
        self.password = password  # Hash de la contraseña
        self.fullname = fullname
        self.active = active

    @classmethod
    def check_password(cls, hashed_password, password):
        return check_password_hash(hashed_password, password)

    def is_active(self):
        return self.active
    
    def is_authenticated(self):
        return True  

    def get_id(self):
        return str(self.id)


