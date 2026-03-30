import React, { useState } from "react";
import { uploadImage } from "./api";

export default function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleUpload = async () => {
    if (!file) return alert("Select image first");

    const data = await uploadImage(file);
    setResult(data);
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Food Freshness Analyzer</h1>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br /><br />

      <button onClick={handleUpload}>Analyze</button>

      {result && (
        <div>
          <h2>Result:</h2>
          <p>Freshness: {result.freshness_class}</p>
          <p>Confidence: {result.confidence}</p>
        </div>
      )}
    </div>
  );
}