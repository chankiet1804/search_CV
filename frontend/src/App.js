import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/Header';
import SearchForm from './components/SearchForm';
import CVList from './components/CVList';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <div className="container mt-4">
          <Routes>
            <Route path="/" element={<SearchForm />} />
            <Route path="/cvs" element={<CVList />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;