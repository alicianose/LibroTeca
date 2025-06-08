from datetime import datetime

class Review:
    def __init__(self, id, user_id, book_id, score, coment, timestamp=None):
        self.id = id
        self.user_id = user_id
        self.book_id = book_id
        self.score = score
        self.coment = coment
        self.timestamp = timestamp or datetime.now()  