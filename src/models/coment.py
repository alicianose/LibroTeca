from datetime import datetime  # Importar la clase datetime directamente
class Coment:
    def __init__(self, id, user_id, review_id, text, timestamp=None):
        self.id = id
        self.user_id = user_id
        self.review_id = review_id
        self.text = text
        self.timestamp = timestamp or datetime.now()  