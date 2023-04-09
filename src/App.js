import React from 'react';
import './App.scss';
import 'bootstrap/dist/css/bootstrap.min.css';
import Chatbot from './components/Chatbot';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Baking Recipe Chatbot</h1>
      </header>
      <Chatbot />
    </div>
  );
}

export default App;
