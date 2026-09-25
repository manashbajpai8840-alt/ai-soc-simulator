"""
Lightweight, deterministic prefilter. Its only job is to cut down how
much gets sent to the LLM — obviously-benign traffic never leaves this
module. Real threat/false-positive *judgment* still happens in
ai_analyzer.py; this file just decides "is this worth asking the AI about?"
"""
import re
import time
from collections import defaultdict

import config

SQLI_PATTERN = re.compile(
    r"(\bunion\b.*\bselect\b|'\s*or\s*'?1'?\s*=\s*'?1|--\s*$|drop\s+table|;\s*drop\b)",
    re.IGNORECASE,
)

_failed_login_window = defaultdict(list)  # ip -> [timestamps]


def _prune_window(ip, now):
    cutoff = now - config.BRUTE_FORCE_WINDOW_SECONDS
    _failed_login_window[ip] = [t for t in _failed_login_window[ip] if t > cutoff]


def is_suspicious(event):
    """
    Returns True if this event's raw_log crosses a simple heuristic
    threshold and should be escalated to the AI analyzer.
    """
    category = event["category"]
    raw = event["raw_log"]
    ip = event["source_ip"]
    now = time.time()

    if category == "sql_injection":
        return bool(SQLI_PATTERN.search(raw))

    if category == "malware_c2":
        # any beacon-shaped connection to a known-odd destination is
        # worth a second look
        return "note=" in raw and "beacon" in raw

    if category == "brute_force":
        _failed_login_window[ip].append(now)
        _prune_window(ip, now)
        return len(_failed_login_window[ip]) >= config.BRUTE_FORCE_THRESHOLD

    return False  # benign traffic never gets flagged
