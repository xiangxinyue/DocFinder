import React from "react";

export default function SearchBar({ role, setRole, query, setQuery, onSearch }) {
  return (
    <div className="search-bar">
      <select value={role} onChange={(e) => setRole(e.target.value)}>
        <option value="QA">QA</option>
        <option value="Dev">Dev</option>
        <option value="Support">Support</option>
        <option value="Business">Business</option>
      </select>
      <input
        type="text"
        placeholder="What do you want to know today?"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={onSearch}>Search</button>
    </div>
  );
}
