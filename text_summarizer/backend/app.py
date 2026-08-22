from flask import Flask, request, jsonify
from flask_cors import CORS
from summarizer import summarize_text, which_engine_used
from keywords import extract_keywords, highlight_keywords
import database

app = Flask(__name__)
CORS(app)  # allow requests from the React dev server (localhost:5173)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

database.init_db()


@app.route("/api/summarize", methods=["POST"])
def summarize():
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    mode = data.get("mode", "short")
    algorithm = data.get("algorithm", "auto")
    length_pct = int(data.get("length_pct", 20))

    if not text:
        return jsonify({"error": "No text provided"}), 400
    if len(text.split()) < 20:
        return jsonify({"error": "Please provide at least ~20 words of text."}), 400

    try:
        summary = summarize_text(text, mode=mode, algorithm=algorithm, length_pct=length_pct)
        engine = which_engine_used(algorithm)
        keywords = extract_keywords(text, top_n=10)
        highlighted_original = highlight_keywords(text, keywords)

        summary_id = database.save_summary(mode, engine, text, summary)

        return jsonify({
            "id": summary_id,
            "summary": summary,
            "engine_used": engine,
            "keywords": keywords,
            "highlighted_original": highlighted_original,
            "original_word_count": len(text.split()),
            "summary_word_count": len(summary.split()),
            "compression_ratio": round(len(summary.split()) / len(text.split()), 3)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = file.filename.lower()

    try:
        if filename.endswith(".txt"):
            text = file.read().decode("utf-8", errors="ignore")
        elif filename.endswith(".pdf"):
            import pdfplumber
            text = ""
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        else:
            return jsonify({"error": "Only .txt and .pdf files are supported"}), 400

        return jsonify({"text": text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history", methods=["GET"])
def api_history():
    rows = database.get_recent(limit=30)
    return jsonify({"history": rows, "stats": database.get_stats()})


@app.route("/api/history/<int:summary_id>", methods=["DELETE"])
def api_delete_history(summary_id):
    database.delete_summary(summary_id)
    return jsonify({"deleted": summary_id})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
