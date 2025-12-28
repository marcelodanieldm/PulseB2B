from models.user import User
import requests

class UserController:
    def __init__(self):
        self.users = []
        self.error = None

    def fetch_users(self):
        try:
            res = requests.get('https://jsonplaceholder.typicode.com/users')
            res.raise_for_status()
            self.users = [User(u['id'], u['name'], u['email']) for u in res.json()]
        except Exception as err:
            self.error = str(err)
        return self.users

    def add_user(self, name, email):
        new_id = max([u.id for u in self.users], default=0) + 1
        user = User(new_id, name, email)
        self.users.append(user)
        return user
