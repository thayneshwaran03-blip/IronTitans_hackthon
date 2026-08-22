jsx
export default function SummaryOutput({ result }) {
  const handleCopy = () => {
    navigator.clipboard.writeText(result.summary);
  };

  return (
    <div className="output-box">
      <div className="output-header">
        <h2>Summary</h2>
        <button onClick={handleCopy}>Copy</button>
      </div>

      <p>{result.summary}</p>

      <div className="stats">
        Original: {result.original_word_count} words → Summary: {result.summary_word_count} words
        {" "}({(result.compression_ratio * 100).toFixed(1)}% of original)
      </div>

      <div className="engine-tag">Engine used: {result.engine_used}</div>

      <details className="keywords-details">
        <summary>Show key terms & highlighted original</summary>
        <div className="keywords-list">
          {result.keywords.map((k, i) => (
            <span key={i} className="keyword-chip">{k}</span>
          ))}
        </div>
        <p
          className="highlighted-text"
          dangerouslySetInnerHTML={{ __html: result.highlighted_original }}
        />
      </details>
    </div>
  );
}


