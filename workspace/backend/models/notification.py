class Notification:
    def __init__(self, id, message, user_type):
        self.id = id
        self.message = message
        self.user_type = user_type  # 'free', 'pro', or 'all'

    def to_dict(self):
        return {'id': self.id, 'message': self.message, 'user_type': self.user_type}
