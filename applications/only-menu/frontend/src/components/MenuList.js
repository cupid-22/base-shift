import React from 'react';

const MenuList = ({ menus }) => {
  return (
    <div className="container">
      <h2>Available Menus</h2>
      <ul>
        {menus.map((menu, index) => (
          <li key={index}>{menu.name} - {menu.description}</li>
        ))}
      </ul>
    </div>
  );
};

export default MenuList;