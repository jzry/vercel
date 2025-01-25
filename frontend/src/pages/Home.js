import React from 'react';
import { Link } from 'react-router-dom';
import '../App.css';

function Home() {
  return (
    <div className="App">
      <div className="button-container">
        <Link to="/bce">
          <button className="scorecard-button">BCE Scorecard</button>
        </Link>
        <Link to="/ctr">
          <button className="scorecard-button">CTR Scorecard</button>
        </Link>
      </div>
    </div>
  );
}

export default Home;
