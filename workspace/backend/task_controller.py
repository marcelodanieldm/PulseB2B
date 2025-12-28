import requests

class TaskController:
    def __init__(self):
        self.tasks = []
        self.loading = False
        self.error = None

    def fetch_tasks(self):
        self.loading = True
        self.error = None
        try:
            res = requests.get('https://jsonplaceholder.typicode.com/todos?_limit=5')
            res.raise_for_status()
            self.tasks = res.json()
        except Exception as err:
            self.error = str(err)
        finally:
            self.loading = False
        return self.tasks

    def add_task(self, title):
        if not title.strip():
            return
        self.tasks.insert(0, {'id': id(self), 'title': title, 'completed': False})

    def toggle_task(self, id):
        for t in self.tasks:
            if t['id'] == id:
                t['completed'] = not t['completed']

    def delete_task(self, id):
        self.tasks = [t for t in self.tasks if t['id'] != id]
