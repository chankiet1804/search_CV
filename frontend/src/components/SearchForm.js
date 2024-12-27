import React, { useState } from 'react';
import CVCard from './CVCard';

function SearchForm() {
  const [jd, setJd] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ jd }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error);
      }

      setResults(data.results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="row justify-content-center">
      <div className="col-md-8">
        <div className="card">
          <div className="card-header">
            <h3 className="text-center">Tìm kiếm CV theo Job Description</h3>
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="jd" className="form-label">
                  Mô tả công việc:
                </label>
                <textarea
                  className="form-control"
                  id="jd"
                  value={jd}
                  onChange={(e) => setJd(e.target.value)}
                  rows="6"
                  required
                />
              </div>
              <div className="text-center">
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Đang tìm...' : 'Tìm kiếm'}
                </button>
              </div>
            </form>
          </div>
        </div>

        {error && (
          <div className="alert alert-danger mt-3">{error}</div>
        )}

        <div className="mt-4">
          {results.map((cv) => (
            <CVCard key={cv.id} cv={cv} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default SearchForm;