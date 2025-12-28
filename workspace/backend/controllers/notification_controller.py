from models.notification import Notification

class NotificationController:
    def __init__(self):
        self.notifications = []
        self.next_id = 1

    def add_notification(self, message, user_type):
        notif = Notification(self.next_id, message, user_type)
        self.notifications.append(notif)
        self.next_id += 1
        return notif

    def get_notifications(self, user_type):
        # Return notifications for the given user_type or 'all'
        return [n for n in self.notifications if n.user_type == user_type or n.user_type == 'all']
