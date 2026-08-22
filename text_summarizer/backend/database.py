
"""
SQLite-backed history log for summaries.
Satisfies: "keep a basic log so patterns can be reviewed" style requirement
and gives you a real feature to demo (history page + stats).
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "summaries.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            mode TEXT NOT NULL,
            algorithm TEXT NOT NULL,
            original_text TEXT NOT NULL,
            summary_text TEXT NOT NULL,
            original_word_count INTEGER NOT NULL,
            summary_word_count INTEGER NOT NULL,
            compression_ratio REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_summary(mode, algorithm, original_text, summary_text):
    original_wc = len(original_text.split())
    summary_wc = len(summary_text.split())
    ratio = round(summary_wc / original_wc, 3) if original_wc else 0

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO summaries
        (created_at, mode, algorithm, original_text, summary_text, original_word_count, summary_word_count, compression_ratio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(timespec="seconds"),
        mode, algorithm, original_text, summary_text, original_wc, summary_wc, ratio
    ))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_recent(limit=20):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM summaries ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), AVG(compression_ratio), SUM(original_word_count), SUM(summary_word_count) FROM summaries")
    count, avg_ratio, total_orig, total_summary = cur.fetchone()
    conn.close()
    return {
        "total_summaries": count or 0,
        "avg_compression_ratio": round(avg_ratio, 3) if avg_ratio else 0,
        "total_words_processed": total_orig or 0,
        "total_words_saved": (total_orig or 0) - (total_summary or 0)
    }


def delete_summary(summary_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM summaries WHERE id = ?", (summary_id,))
    conn.commit()
    conn.close()


