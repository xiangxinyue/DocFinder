import React, { useState } from 'react';
import axios from 'axios';
import SearchBar from './components/SearchBar';
import ResultCard from './components/ResultCard';
import './App.css';

function App() {
  const [role, setRole] = useState("QA");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    // Clear previous results and errors
    setResults([]);
    setError("");
    
    try {
      // Fix: remove the duplicate await
      const response = await axios.post("https://docfinder-ncrl.onrender.com/query", {
        query: query
      }, {
        // Add explicit headers to help with CORS
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (response.data && response.data.matches) {
        setResults(response.data.matches);
      } else {
        setError("Received an unexpected response format");
      }
    } catch (err) {
      console.error("Search failed", err);
      setError(`Search failed: ${err.message || "Unknown error"}`);
    }
  };

  return (
    <div className="app-container">
      <h1>DocFinder</h1>
      <SearchBar
        role={role}
        setRole={setRole}
        query={query}
        setQuery={setQuery}
        onSearch={handleSearch}
      />
      
      {error && <div className="error-message">{error}</div>}
      
      <h3>{results.length} matches found</h3>
      {results.map((res, i) => (
        <ResultCard key={i} result={res} />
      ))}
    </div>
  );
}

export default App;