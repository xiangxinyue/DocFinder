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
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError("Please enter a search query");
      return;
    }
    
    // Clear previous results and errors
    setResults([]);
    setError("");
    setIsLoading(true);
    
    try {
      // Use local API proxy instead of calling remote API directly
      const response = await axios.post("https://docfinder-ncrl.onrender.com/query", {
        query: query
      });
      
      if (response.data && response.data.matches) {
        setResults(response.data.matches);
      } else {
        setError("Received unexpected response format");
      }
    } catch (err) {
      console.error("Search failed", err);
      setError(`Search failed: ${err.message || "Unknown error"}`);
    } finally {
      setIsLoading(false);
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
        isLoading={isLoading}
      />
      
      {error && <div className="error-message">{error}</div>}
      
      {isLoading ? (
        <div className="loading-indicator">Searching...</div>
      ) : (
        <>
          <h3>{results.length} matches found</h3>
          {results.map((res, i) => (
            <ResultCard key={i} result={res} />
          ))}
        </>
      )}
    </div>
  );
}

export default App;