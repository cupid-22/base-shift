import React from 'react';
import { useLocation } from 'react-router-dom';

const Rewards = () => {
  const location = useLocation();
  const uploadedFile = location.state?.uploadedFile || 'No file uploaded yet';

  return (
    <div className="rewards">
      <h2>Your Rewards</h2>
      <p>Congratulations! You have earned rewards for uploading a menu.</p>
      {uploadedFile && (
        <div>
          <h3>Your Uploaded Menu:</h3>
          <p>{uploadedFile}</p>
        </div>
      )}
    </div>
  );
};

export default Rewards;
