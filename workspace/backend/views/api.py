from flask import Blueprint, jsonify, request
from controllers.user_controller import UserController
from controllers.task_controller import TaskController

api = Blueprint('api', __name__)
user_controller = UserController()
task_controller = TaskController()

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
