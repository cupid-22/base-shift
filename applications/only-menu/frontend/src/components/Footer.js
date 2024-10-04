// src/components/Footer.js

import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-links">
          <Link to="/sitemap">Site Map</Link>
          <Link to="/contact-us">Contact Us</Link>
          <Link to="/get-quote">Get a Quote</Link>
          <Link to="/faq">FAQ</Link>
        </div>
        <p className="footer-copy">&copy; 2024 Only Menu. All rights reserved.</p>
      </div>
    </footer>
  );
}

export default Footer;
