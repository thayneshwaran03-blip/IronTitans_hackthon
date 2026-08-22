jsx
import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = "http://127.0.0.1:5000/api";

export default function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);

  const loadHistory = async () => {
    const res = await axios.get(`${API_BASE}/history`);
    setHistory(res.data.history);
    setStats(res.data.stats);
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleDelete = async (id) => {
    await axios.delete(`${API_BASE}/history/${id}`);
    loadHistory();
  };

  return (
    <div>
      {stats && (
        <div className="stats-bar">
          <div className="stat-card"><strong>{stats.total_summaries}</strong><span>Total Summaries</span></div>
          <div className="stat-card"><strong>{stats.avg_compression_ratio}</strong><span>Avg Compression Ratio</span></div>
          <div className="stat-card"><strong>{stats.total_words_processed}</strong><span>Words Processed</span></div>
          <div className="stat-card"><strong>{stats.total_words_saved}</strong><span>Words Saved</span></div>
        </div>
      )}

      <div className="history-list">
        {history.map((item) => (
          <div className="history-item" key={item.id}>
            <div className="history-meta">
              <span>{item.created_at}</span>
              <span className="tag">{item.mode}</span>
              <span className="tag">{item.algorithm}</span>
              <button className="delete-btn" onClick={() => handleDelete(item.id)}>Delete</button>
            </div>
            <p className="history-summary">{item.summary_text}</p>
            <div className="history-stats">
              {item.original_word_count} → {item.summary_word_count} words ({item.compression_ratio})
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


