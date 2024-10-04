// src/components/UploadMenu.js

import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { uploadMenu } from '../redux/actions';
import '../assets/UploadMenu.css';

function UploadMenu() {
  const [menuName, setMenuName] = useState('');
  const [menuFile, setMenuFile] = useState(null);
  const dispatch = useDispatch();

  const handleUpload = () => {
    if (menuName && menuFile) {
      const newMenu = {
        name: menuName,
        file: menuFile.name,
      };
      dispatch(uploadMenu(newMenu));
      setMenuName('');
      setMenuFile(null);
      alert('Menu uploaded successfully!');
    } else {
      alert('Please fill in all fields.');
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload a New Menu</h2>
      <input
        type="text"
        placeholder="Menu Name"
        value={menuName}
        onChange={(e) => setMenuName(e.target.value)}
      />
      <input
        type="file"
        onChange={(e) => setMenuFile(e.target.files[0])}
      />
      <button className="upload-button" onClick={handleUpload}>
        Upload Menu
      </button>
    </div>
  );
}

export default UploadMenu;
