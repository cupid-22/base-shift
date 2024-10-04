import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './components/NavBar';
import Footer from './components/Footer';
import Home from './components/Home';
import ViewMenu from './components/ViewMenu';
import UploadMenu from './components/UploadMenu';
import Rewards from './components/Rewards';
import Login from './components/Login';
import NotFound from './components/NotFound'; // Import the NotFound component
import './assets/App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/view" element={<ViewMenu />} />
            <Route path="/upload" element={<UploadMenu />} />
            <Route path="/rewards" element={<Rewards />} />
            <Route path="/login" element={<Login />} />
            <Route path="*" element={<NotFound />} /> {/* Use NotFound component */}
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
