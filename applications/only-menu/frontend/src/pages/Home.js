import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div className="container">
      <h1>Welcome to Only Menus</h1>
      <p>Upload restaurant menus and earn rewards!</p>
      <Link to="/upload"><button>Upload Menu</button></Link>
      <Link to="/menus"><button>View Menus</button></Link>
    </div>
  );
};

export default Home;