import { useState, useEffect } from "react";
import Upload from "./components/Upload";
import Camera from "./components/Camera";
import Result from "./components/Result";
import History from "./components/History";
import "./App.css";

function App() {
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem("history")) || [];
    setHistory(saved);
  }, []);

  const updateHistory = (data) => {
    const newHistory = [data, ...history];
    setHistory(newHistory);
    localStorage.setItem("history", JSON.stringify(newHistory));
  };

  return (
    <div className="container">
      <h1 className="title">🥗 Smart Food Quality Analyzer</h1>

      <div className="buttonRow">
        <Upload setResult={setResult} updateHistory={updateHistory} />
        <Camera setResult={setResult} updateHistory={updateHistory} />
      </div>

      {result && <Result data={result} />}

      {/* Green History Button */}
      <div className="historyCard" onClick={() => setShowHistory(!showHistory)}>
        📜 View History
      </div>

      {/* Show history only when clicked */}
      {showHistory && <History history={history} />}
    </div>
  );
}

export default App;