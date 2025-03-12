import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import GetPhotos from './pages/CTR/GetPhotos';
import BCE from './pages/BCE/BCE';
import Corners from './pages/Test/Corners';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/ctr" element={< GetPhotos/>} />
        <Route path="/bce" element={< BCE/>} />
        <Route path="/corners" element={< Corners/>} />
      </Routes>
    </Router>
  );
}

export default App;
