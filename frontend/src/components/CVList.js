import React, { useState, useEffect } from 'react';
import CVCard from './CVCard';

function CVList() {
  const [cvs, setCvs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCVs();
  }, []);

  const fetchCVs = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/cvs');
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error);
      }
      setCvs(data.cvs);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Đang tải...</div>;
  if (error) return <div className="alert alert-danger">{error}</div>;

  return (
    <div>
      <h3>Danh sách CV</h3>
      {cvs.map((cv) => (
        <CVCard key={cv.id} cv={cv} />
      ))}
    </div>
  );
}

export default CVList;