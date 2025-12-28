# Simple in-memory user store for demo
USERS = [
    {"username": "superadmin", "password": "superpass", "role": "superadmin"},
    {"username": "clientepro", "password": "propass", "role": "clientepro"}
]

def authenticate(username, password):
    for user in USERS:
        if user["username"] == username and user["password"] == password:
            return {"username": user["username"], "role": user["role"]}
    return None
