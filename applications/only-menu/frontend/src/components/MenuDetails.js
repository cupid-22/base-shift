import React from 'react';

function MenuDetails() {
  return (
    <div className="menu-details">
      <h1>Restaurant Name</h1>
      <p>Menu details and description</p>
      <div className="menu-items">
        <div className="menu-item-detail">
          <h2>Dish 1</h2>
          <p>Description of Dish 1</p>
        </div>
        <div className="menu-item-detail">
          <h2>Dish 2</h2>
          <p>Description of Dish 2</p>
        </div>
      </div>
    </div>
  );
}

export default MenuDetails;
