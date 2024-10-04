// src/components/SearchMenu.js

import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import './SearchMenu.css';

function SearchMenu() {
  const [searchTerm, setSearchTerm] = useState('');
  const menus = useSelector(state => state.menu.menus);

  const filteredMenus = menus.filter(menu =>
    menu.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="search-container">
      <h2>Search Menus</h2>
      <input
        type="text"
        placeholder="Search for a menu..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      <div className="menu-results">
        {filteredMenus.length > 0 ? (
          filteredMenus.map((menu, index) => (
            <div className="menu-item" key={index}>
              <h3>{menu.name}</h3>
              <p>Uploaded File: {menu.file}</p>
            </div>
          ))
        ) : (
          <p>No menus found.</p>
        )}
      </div>
    </div>
  );
}

export default SearchMenu;
