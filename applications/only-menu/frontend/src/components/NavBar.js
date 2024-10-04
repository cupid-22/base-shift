// src/components/NavBar.js

import React from 'react';
import { useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import '../assets/NavBar.css';
import logo from '../static/images/logo.png';
import profileIcon from '../static/images/profile.png';

function NavBar() {
  const username = useSelector(state => state.user?.username || 'Guest');

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <img src={logo} alt="Only Menu Logo" />
        </Link>
        <div className="navbar-links">
          <Link to="/upload">Upload Menu</Link>
          <Link to="/view-reward">View Reward</Link>
          <Link to="/search-menu">Search Menu</Link>
        </div>
        <div className="navbar-user">
          <span className="navbar-username">{username}</span>
          <img src={profileIcon} alt="Profile" className="navbar-profile-icon" />
        </div>
      </div>
    </nav>
  );
}

export default NavBar;
