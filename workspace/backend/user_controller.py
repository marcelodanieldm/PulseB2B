import requests

class UserController:
    def __init__(self):
        self.users = []
        self.loading = False
        self.error = None

    def fetch_users(self):
        self.loading = True
        self.error = None
        try:
            res = requests.get('https://jsonplaceholder.typicode.com/users')
            res.raise_for_status()
            self.users = res.json()
        except Exception as err:
            self.error = str(err)
        finally:
            self.loading = False
        return self.users
