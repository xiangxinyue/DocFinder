import React from "react";

export default function ResultCard({ result }) {
  return (
    <div className="result-card">
      <p>“{result.text}”</p>
      <p><strong>{result.title}</strong></p>
      <div className="card-links">
        <a href={result.url || "#"} target="_blank" rel="noreferrer">🔗 View source</a>
        &nbsp;&nbsp;
        <a href="#" onClick={() => navigator.clipboard.writeText(result.text)}>📋 Copy ref</a>
      </div>
    </div>
  );
}
