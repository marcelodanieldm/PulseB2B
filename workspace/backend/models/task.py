class Task:
    def __init__(self, id, title, completed=False):
        self.id = id
        self.title = title
        self.completed = completed

    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'completed': self.completed}
