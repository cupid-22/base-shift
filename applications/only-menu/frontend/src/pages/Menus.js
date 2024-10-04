import React, { useState, useEffect } from 'react';
import MenuList from '../components/MenuList';

const Menus = () => {
  const [menus, setMenus] = useState([]);

  useEffect(() => {
    // Fetch menus from API
    const fetchMenus = async () => {
      try {
        const response = await axios.get('/api/menus');
        setMenus(response.data);
      } catch (error) {
        console.error('Error fetching menus:', error);
      }
    };

    fetchMenus();
  }, []);

  return (
    <div className="container">
      <MenuList menus={menus} />
    </div>
  );
};

export default Menus;