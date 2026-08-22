import { useState } from "react";
import SummarizerForm from "./components/SummarizerForm";
import SummaryOutput from "./components/SummaryOutput";
import HistoryPage from "./components/HistoryPage";

export default function App() {
    const [view, setView] = useState("summarizer");
    const [result, setResult] = useState(null);

    return (
        <div className="container">
            <div className="top-bar">
                <h1>📄 Automatic Text Summarizer</h1>
                <button className="link-btn" onClick={() => setView(view === "summarizer" ? "history" : "summarizer")}>
                    {view === "summarizer" ? "View History →" : "← Back to Summarizer"}
                </button>
            </div>

            {view === "summarizer" ? (
                <>
                    <p className="subtitle">
                        Paste a long article, circular, or study material below and get a quick, accurate summary.
                    </p>
                    <SummarizerForm onResult={setResult} />
                    {result && <SummaryOutput result={result} />}
                </>
            ) : (
                <HistoryPage />
            )}
        </div>
    );
}