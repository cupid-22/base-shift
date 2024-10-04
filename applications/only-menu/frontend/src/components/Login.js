import React from 'react';
//import React, { useState } from 'react';
//import { useDispatch } from 'react-redux';
//import { setUsername } from '../redux/userSlice';
//import { useNavigate } from 'react-router-dom';
import '../assets/Login.css';

function Login() {
//  const [username, setUsername] = useState('');
//  const dispatch = useDispatch();
//  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    // Dummy login logic
    const username = e.target.username.value;
    localStorage.setItem('username', username);
    window.location.href = '/';
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Login</h2>
        <form onSubmit={handleLogin}>
          <input type="text" name="username" placeholder="Username" required />
          <input type="password" name="password" placeholder="Password" required />
          <button type="submit">Login</button>
        </form>
        <div className="sso-options">
          <button>Sign in with Google</button>
          <button>Sign in with Facebook</button>
        </div>
      </div>
    </div>
  );
}

export default Login;
