import React, { useState } from 'react';
import axios from 'axios';
import SearchBar from './components/SearchBar';
import ResultCard from './components/ResultCard';

import './App.css';

function App() {
  const [role, setRole] = useState("QA");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    try {
      const response = await await axios.post("https://docfinder-ncrl.onrender.com/query", { //axios.post("http://localhost:8000/query"
        query: query
      });
      setResults(response.data.matches);
    } catch (err) {
      console.error("Search failed", err);
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
      <h3>{results.length} matches found</h3>
      {results.map((res, i) => (
        <ResultCard key={i} result={res} />
      ))}
    </div>
  );
}

export default App;
