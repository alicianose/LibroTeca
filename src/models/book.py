class Book:
     def __init__(self, id, title, author, descr, cover, genre, addedby):
        self.id = id
        self.title = title
        self.author = author
        self.descr = descr
        self.cover = cover
        self.genre = genre
        self.addedby = addedby

@property
def id(self):
    return self._id