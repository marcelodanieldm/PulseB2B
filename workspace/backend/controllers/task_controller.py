from models.task import Task
import requests

class TaskController:
    def __init__(self):
        self.tasks = []
        self.error = None

    def fetch_tasks(self):
        try:
            res = requests.get('https://jsonplaceholder.typicode.com/todos?_limit=5')
            res.raise_for_status()
            self.tasks = [Task(t['id'], t['title'], t['completed']) for t in res.json()]
        except Exception as err:
            self.error = str(err)
        return self.tasks

    def add_task(self, title):
        new_id = max([t.id for t in self.tasks], default=0) + 1
        task = Task(new_id, title, False)
        self.tasks.insert(0, task)
        return task

    def toggle_task(self, id):
        for t in self.tasks:
            if t.id == id:
                t.completed = not t.completed
                return t
        return None

    def delete_task(self, id):
        self.tasks = [t for t in self.tasks if t.id != id]
