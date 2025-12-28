from flask import Flask, jsonify, request
from user_controller import UserController
from task_controller import TaskController

app = Flask(__name__)
user_controller = UserController()
task_controller = TaskController()

@app.route('/api/users', methods=['GET'])
def get_users():
    users = user_controller.fetch_users()
    if user_controller.error:
        return jsonify({'error': user_controller.error}), 500
    return jsonify(users)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = task_controller.fetch_tasks()
    if task_controller.error:
        return jsonify({'error': task_controller.error}), 500
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    title = data.get('title', '')
    task_controller.add_task(title)
    return jsonify({'status': 'ok'})

@app.route('/api/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    task_controller.toggle_task(task_id)
    return jsonify({'status': 'ok'})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task_controller.delete_task(task_id)
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True)
