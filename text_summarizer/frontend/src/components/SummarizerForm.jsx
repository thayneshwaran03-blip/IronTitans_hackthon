jsx
import { useState } from "react";
import axios from "axios";

const API_BASE = "http://127.0.0.1:5000/api";

export default function SummarizerForm({ onResult }) {
  const [text, setText] = useState("");
  const [mode, setMode] = useState("short");
  const [algorithm, setAlgorithm] = useState("auto");
  const [lengthPct, setLengthPct] = useState(20);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [fileName, setFileName] = useState("");

  const lengthLabel = lengthPct <= 15 ? "Short" : lengthPct <= 28 ? "Medium" : "Long";

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setFileName(file.name);

    const formData = new FormData();
    formData.append("file", file);

    setStatus("Extracting text from file...");
    try {
      const res = await axios.post(`${API_BASE}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      if (res.data.error) {
        setStatus("Error: " + res.data.error);
        return;
      }
      setText(res.data.text);
      setStatus("File loaded. Click Summarize.");
    } catch (err) {
      setStatus("Failed to read file: " + err.message);
    }
  };

  const handleSummarize = async () => {
    if (!text.trim()) {
      setStatus("Please paste or upload some text first.");
      return;
    }

    setLoading(true);
    setStatus("Summarizing... (this may take a few seconds)");
    onResult(null);

    try {
      const res = await axios.post(`${API_BASE}/summarize`, {
        text,
        mode,
        algorithm,
        length_pct: lengthPct,
      });

      if (res.data.error) {
        setStatus("Error: " + res.data.error);
      } else {
        onResult(res.data);
        setStatus("");
      }
    } catch (err) {
      setStatus("Request failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="input-row">
        <label htmlFor="fileInput" className="file-btn">Upload .txt / .pdf</label>
        <input type="file" id="fileInput" accept=".txt,.pdf" hidden onChange={handleFileUpload} />
        <span>{fileName}</span>
      </div>

      <textarea
        rows={12}
        placeholder="Paste your long text here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <div className="controls">
        <div className="mode-toggle">
          <label>
            <input type="radio" name="mode" checked={mode === "short"} onChange={() => setMode("short")} />
            Short
          </label>
          <label>
            <input type="radio" name="mode" checked={mode === "detailed"} onChange={() => setMode("detailed")} />
            Detailed
          </label>
        </div>

        <div className="algo-select">
          <label htmlFor="algorithm">Engine:</label>
          <select id="algorithm" value={algorithm} onChange={(e) => setAlgorithm(e.target.value)}>
            <option value="auto">Auto (best available)</option>
            <option value="transformer">Transformer (AI)</option>
            <option value="textrank">Extractive - TextRank</option>
            <option value="lsa">Extractive - LSA</option>
            <option value="luhn">Extractive - Luhn</option>
          </select>
        </div>

        <button onClick={handleSummarize} disabled={loading}>
          {loading ? "Summarizing..." : "Summarize"}
        </button>
      </div>

      <div className="slider-row">
        <label>Summary length: {lengthLabel}</label>
        <input
          type="range"
          min="10"
          max="40"
          value={lengthPct}
          onChange={(e) => setLengthPct(parseInt(e.target.value))}
        />
      </div>

      <div id="status">{status}</div>
    </div>
  );
}
