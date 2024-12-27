import React from 'react';
import { Link } from 'react-router-dom';

function Header() {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <Link className="navbar-brand" to="/">CV Search</Link>
        <div className="navbar-nav">
          <Link className="nav-link" to="/">Tìm kiếm</Link>
          <Link className="nav-link" to="/cvs">Danh sách CV</Link>
        </div>
      </div>
    </nav>
  );
}

export default Header;