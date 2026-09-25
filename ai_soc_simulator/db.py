"""
Thin SQLite wrapper used as the shared state store between the
log generator / analyzer / responder processes and the dashboard.
"""
import json
import sqlite3
import time
from contextlib import contextmanager

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    source_ip TEXT,
    category TEXT,              -- brute_force | sql_injection | malware_c2 | benign
    raw_log TEXT NOT NULL,
    prefilter_flagged INTEGER NOT NULL DEFAULT 0,
    ai_reviewed INTEGER NOT NULL DEFAULT 0,
    ai_verdict TEXT,            -- real_threat | false_positive | null
    ai_confidence REAL,
    ai_reasoning TEXT,
    response_action TEXT,       -- blocked_ip | isolated_process | none
    response_mode TEXT,         -- simulated | live
    forensic_report_path TEXT
);

CREATE TABLE IF NOT EXISTS blocked_ips (
    ip TEXT PRIMARY KEY,
    blocked_at REAL NOT NULL,
    expires_at REAL NOT NULL,
    mode TEXT NOT NULL          -- simulated | live
);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(config.DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def insert_event(source_ip, category, raw_log, prefilter_flagged):
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO events (ts, source_ip, category, raw_log, prefilter_flagged)
               VALUES (?, ?, ?, ?, ?)""",
            (time.time(), source_ip, category, raw_log, int(prefilter_flagged)),
        )
        return cur.lastrowid


def update_ai_verdict(event_id, verdict, confidence, reasoning):
    with get_conn() as conn:
        conn.execute(
            """UPDATE events SET ai_reviewed = 1, ai_verdict = ?, ai_confidence = ?,
               ai_reasoning = ? WHERE id = ?""",
            (verdict, confidence, reasoning, event_id),
        )


def update_response(event_id, action, mode, forensic_report_path=None):
    with get_conn() as conn:
        conn.execute(
            """UPDATE events SET response_action = ?, response_mode = ?,
               forensic_report_path = ? WHERE id = ?""",
            (action, mode, forensic_report_path, event_id),
        )


def add_blocked_ip(ip, mode):
    now = time.time()
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO blocked_ips (ip, blocked_at, expires_at, mode)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(ip) DO UPDATE SET blocked_at=excluded.blocked_at,
               expires_at=excluded.expires_at, mode=excluded.mode""",
            (ip, now, now + config.BLOCK_DURATION_SECONDS, mode),
        )


def get_active_blocks():
    now = time.time()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM blocked_ips WHERE expires_at > ? ORDER BY blocked_at DESC", (now,)
        ).fetchall()
        return [dict(r) for r in rows]


def is_ip_blocked(ip):
    now = time.time()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM blocked_ips WHERE ip = ? AND expires_at > ?", (ip, now)
        ).fetchone()
        return row is not None


def get_recent_events(limit=200):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM events ORDER BY ts DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_stats():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) c FROM events").fetchone()["c"]
        flagged = conn.execute(
            "SELECT COUNT(*) c FROM events WHERE prefilter_flagged = 1"
        ).fetchone()["c"]
        threats = conn.execute(
            "SELECT COUNT(*) c FROM events WHERE ai_verdict = 'real_threat'"
        ).fetchone()["c"]
        false_pos = conn.execute(
            "SELECT COUNT(*) c FROM events WHERE ai_verdict = 'false_positive'"
        ).fetchone()["c"]
        blocked = conn.execute(
            "SELECT COUNT(*) c FROM blocked_ips WHERE expires_at > ?", (time.time(),)
        ).fetchone()["c"]
        by_category = conn.execute(
            """SELECT category, COUNT(*) c FROM events
               WHERE ai_verdict = 'real_threat' GROUP BY category"""
        ).fetchall()
        return {
            "total_events": total,
            "prefilter_flagged": flagged,
            "confirmed_threats": threats,
            "false_positives": false_pos,
            "active_blocks": blocked,
            "threats_by_category": {r["category"]: r["c"] for r in by_category},
        }
