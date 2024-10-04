// src/components/ViewRewards.js

import React from 'react';
import { useSelector } from 'react-redux';
import './ViewRewards.css';

function ViewRewards() {
  const menus = useSelector(state => state.menu.menus);

  return (
    <div className="rewards-container">
      <h2>My Rewards</h2>
      {menus.length > 0 ? (
        menus.map((menu, index) => (
          <div className="reward-card" key={index}>
            <h3>{menu.name}</h3>
            <p>Uploaded File: {menu.file}</p>
            <p><strong>Reward Points:</strong> 100</p>
            <button className="redeem-button">Redeem Now</button>
          </div>
        ))
      ) : (
        <p>No rewards available yet.</p>
      )}
    </div>
  );
}

export default ViewRewards;
