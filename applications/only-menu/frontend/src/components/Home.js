import React from 'react';
import { Link } from 'react-router-dom';
import '../assets/Home.css';

const Home = () => {
  return (
    <div className="card-container">
      <Link to="/view">
        <div className="card">
          <div className="card-inner">
            <div className="card-front">
              <img src="/images/view-menu.png" alt="View Menu" className="card-image"/>
              <p>View/Search Menu</p>
            </div>
            <div className="card-back">
              Explore restaurant menus.
            </div>
          </div>
        </div>
      </Link>
      <Link to="/upload">
        <div className="card">
          <div className="card-inner">
            <div className="card-front">
              <img src="/images/upload-menu.png" alt="Upload Menu" className="card-image"/>
              <p>Upload Menu</p>
            </div>
            <div className="card-back">
              Upload a menu and earn rewards.
            </div>
          </div>
        </div>
      </Link>
      <Link to="/rewards">
        <div className="card">
          <div className="card-inner">
            <div className="card-front">
              <img src="/images/view-rewards.png" alt="View Rewards" className="card-image"/>
              <p>View Rewards</p>
            </div>
            <div className="card-back">
              See your earned rewards.
            </div>
          </div>
        </div>
      </Link>
    </div>
  );
};

export default Home;
