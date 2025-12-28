from flask import Blueprint, jsonify, request, session
from controllers.user_controller import UserController
from controllers.task_controller import TaskController
from controllers.notification_controller import NotificationController
from models.auth import authenticate

api = Blueprint('api', __name__)
user_controller = UserController()
task_controller = TaskController()
notification_controller = NotificationController()
@api.route('/notifications', methods=['POST'])
def send_notification():
    data = request.get_json()
    message = data.get('message', '').strip()
    user_type = data.get('user_type', 'all')
    if not message:
        return jsonify({'error': 'El mensaje no puede estar vacío.'}), 400
    notif = notification_controller.add_notification(message, user_type)
    return jsonify(notif.to_dict()), 201

@api.route('/notifications', methods=['GET'])
def get_notifications():
    user_type = request.args.get('user_type', 'all')
    notifs = notification_controller.get_notifications(user_type)
    return jsonify([n.to_dict() for n in notifs])

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    user = authenticate(username, password)
    if user:
        session['user'] = user
        return jsonify({"success": True, "role": user["role"], "username": user["username"]})
    return jsonify({"success": False, "error": "Credenciales inválidas"}), 401

@api.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"success": True})

@api.route('/me', methods=['GET'])
def me():
    user = session.get('user')
    if user:
        return jsonify(user)
    return jsonify({"error": "No autenticado"}), 401

@api.route('/users', methods=['GET'])
def get_users():
    users = user_controller.fetch_users()
    if user_controller.error:
        return jsonify({'error': user_controller.error}), 500
    return jsonify([u.to_dict() for u in users])

@api.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get('name', '')
    email = data.get('email', '')
    user = user_controller.add_user(name, email)
    return jsonify(user.to_dict()), 201

@api.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = task_controller.fetch_tasks()
    if task_controller.error:
        return jsonify({'error': task_controller.error}), 500
    return jsonify([t.to_dict() for t in tasks])

@api.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    title = data.get('title', '')
    task = task_controller.add_task(title)
    return jsonify(task.to_dict()), 201

@api.route('/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    task = task_controller.toggle_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task.to_dict())

@api.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task_controller.delete_task(task_id)
    return jsonify({'status': 'ok'})
