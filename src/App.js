import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Register from './Register'; // Importer la page d'inscription


// URL de l'API FastAPI
const API_URL = 'http://127.0.0.1:8000';

function App() {
  // États pour stocker les items et le message de l'input
  const [items, setItems] = useState([]);
  const [message, setMessage] = useState('');
  const [token, setToken] = useState('');

  // Fonction pour récupérer les items via l'API
  const fetchItems = async () => {
    try {
      const response = await axios.get(`${API_URL}/items/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      setItems(response.data);
    } catch (error) {
      console.error('Error fetching items:', error);
    }
  };

  // Fonction pour ajouter un item
  const addItem = async () => {
    try {
      const response = await axios.post(
        `${API_URL}/items/`,
        { message },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      setMessage(''); // Clear the input field
      fetchItems(); // Refresh the list of items
    } catch (error) {
      console.error('Error adding item:', error);
    }
  };

  // Fonction pour gérer la soumission du formulaire de connexion
  const handleLogin = async (e) => {
    e.preventDefault();
    const username = e.target.username.value;
    const password = e.target.password.value;

    try {
      const response = await axios.post(`${API_URL}/token`, {
        username,
        password,
      });
      setToken(response.data.access_token); // Sauvegarder le token
      fetchItems(); // Charger les items après la connexion
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  useEffect(() => {
    // Si un token est disponible, on charge les items
    if (token) {
      fetchItems();
    }
  }, [token]);

  return (
    <Router>
      <div>
        <h1>FastAPI Items with React</h1>

        {/* Formulaire de connexion */}
        {!token && (
          <form onSubmit={handleLogin}>
            <input type="text" name="username" placeholder="Username" required />
            <input
              type="password"
              name="password"
              placeholder="Password"
              required
            />
            <button type="submit">Login</button>
          </form>
        )}

        {/* Liste des items */}
        {token && (
          <div>
            <h2>Items List</h2>
            <ul>
              {items.map((item, index) => (
                <li key={index}>{item.message}</li>
              ))}
            </ul>

            {/* Formulaire pour ajouter un item */}
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Add a new message"
            />
            <button onClick={addItem}>Add Item</button>
          </div>
        )}

        {/* Routes */}
        <Routes>
          <Route path="/register" element={<Register />} />
          {/* Ajoute d'autres routes si nécessaire */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
