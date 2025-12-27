
import { useEffect, useState } from 'react';
import './App.css';

// Simula una API REST
const API_URL = 'https://jsonplaceholder.typicode.com/todos?_limit=5';

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newTask, setNewTask] = useState('');
  const [alert, setAlert] = useState(null);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(API_URL);
      if (!res.ok) throw new Error('Error al cargar tareas');
      const data = await res.json();
      setTasks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTask = (e) => {
    e.preventDefault();
    if (!newTask.trim()) return;
    // Simula POST a backend
    const fakeTask = { id: Date.now(), title: newTask, completed: false };
    setTasks([fakeTask, ...tasks]);
    setNewTask('');
    setAlert({ type: 'success', msg: 'Tarea agregada' });
    setTimeout(() => setAlert(null), 2000);
  };

  const handleToggle = (id) => {
    setTasks(tasks.map(t => t.id === id ? { ...t, completed: !t.completed } : t));
  };

  const handleDelete = (id) => {
    setTasks(tasks.filter(t => t.id !== id));
    setAlert({ type: 'danger', msg: 'Tarea eliminada' });
    setTimeout(() => setAlert(null), 2000);
  };

  return (
    <div className="container">
      <h1 className="my-4 text-center">Gestión de Tareas</h1>
      {alert && (
        <div className={`alert alert-${alert.type} alert-dismissible fade show`} role="alert">
          {alert.msg}
        </div>
      )}
      <form className="mb-4" onSubmit={handleAddTask}>
        <div className="input-group">
          <input
            type="text"
            className="form-control"
            placeholder="Nueva tarea"
            value={newTask}
            onChange={e => setNewTask(e.target.value)}
          />
          <button className="btn btn-success" type="submit">Agregar</button>
        </div>
      </form>
      {loading ? (
        <div className="text-center my-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando...</span>
          </div>
        </div>
      ) : error ? (
        <div className="alert alert-danger">{error}</div>
      ) : (
        <table className="table table-striped table-hover">
          <thead>
            <tr>
              <th>#</th>
              <th>Tarea</th>
              <th>Completada</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task, idx) => (
              <tr key={task.id} className={task.completed ? 'table-success' : ''}>
                <td>{idx + 1}</td>
                <td>{task.title}</td>
                <td>
                  <input
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => handleToggle(task.id)}
                  />
                </td>
                <td>
                  <button className="btn btn-sm btn-danger" onClick={() => handleDelete(task.id)}>
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default App;
