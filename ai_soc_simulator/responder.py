"""
Automated response actions taken once the AI confirms a real threat.

SAFETY MODEL
------------
Every action here has a `live` flag. When live=False (the default,
config.LIVE_RESPONSE), nothing on the real system is touched: the exact
command that *would* run is logged and returned instead. This is meant
to be demoed and iterated on safely; flip config.LIVE_RESPONSE (and pass
--live on the CLI, and run with the privileges iptables needs) only once
you've reviewed what it does and are running it in an environment where
you're comfortable it firewalls your actual machine.
"""
import json
import os
import shlex
import subprocess
import time

import config


def block_ip(ip: str, live: bool = False) -> dict:
    """
    Blocks (or simulates blocking) an attacker IP with iptables.
    Returns {"mode": "live"|"simulated", "command": "...", "success": bool, "detail": "..."}
    """
    cmd = ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]
    cmd_str = " ".join(shlex.quote(c) for c in cmd)

    if not live:
        return {
            "mode": "simulated",
            "command": cmd_str,
            "success": True,
            "detail": "Simulated only — no firewall rule was actually applied.",
        }

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        success = result.returncode == 0
        detail = result.stderr.strip() or result.stdout.strip() or "iptables rule applied."
        if not success and "not running as root" not in detail.lower():
            detail += " (iptables usually requires root — try running with sudo.)"
        return {"mode": "live", "command": cmd_str, "success": success, "detail": detail}
    except FileNotFoundError:
        return {
            "mode": "live",
            "command": cmd_str,
            "success": False,
            "detail": "iptables binary not found on this system (are you on Linux?).",
        }
    except Exception as e:  # noqa: BLE001
        return {"mode": "live", "command": cmd_str, "success": False, "detail": str(e)}


def isolate_process(pid: int | None, process_name: str, live: bool = False) -> dict:
    """
    "Isolates" a suspicious local process. In simulate mode this just
    logs the intended kill/suspend action. In live mode it sends SIGSTOP
    (pause, not kill, so you can still inspect it) to the given PID if
    one was supplied and actually exists.
    """
    target = f"pid={pid}" if pid else f"process_name={process_name}"
    cmd_str = f"kill -STOP {pid}" if pid else f"(no pid available for {process_name})"

    if not live:
        return {
            "mode": "simulated",
            "command": cmd_str,
            "success": True,
            "detail": f"Simulated isolation of {target} — no real process was touched.",
        }

    if not pid:
        return {
            "mode": "live",
            "command": cmd_str,
            "success": False,
            "detail": "No real PID available to isolate (this event was synthetic).",
        }

    try:
        os.kill(pid, 19)  # SIGSTOP
        return {"mode": "live", "command": cmd_str, "success": True, "detail": f"Sent SIGSTOP to pid {pid}."}
    except ProcessLookupError:
        return {"mode": "live", "command": cmd_str, "success": False, "detail": f"No such pid {pid}."}
    except PermissionError:
        return {"mode": "live", "command": cmd_str, "success": False, "detail": "Permission denied."}


def generate_forensic_report(event: dict, ai_result: dict, response_result: dict) -> str:
    """
    Writes a JSON forensic report for one confirmed incident and returns
    its file path.
    """
    os.makedirs(config.FORENSICS_DIR, exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%S")
    filename = f"incident_{ts}_{event.get('source_ip','unknown').replace('.', '-')}.json"
    path = os.path.join(config.FORENSICS_DIR, filename)

    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "event": {
            "category": event.get("category"),
            "source_ip": event.get("source_ip"),
            "raw_log": event.get("raw_log"),
        },
        "ai_analysis": ai_result,
        "response_taken": response_result,
    }
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    return path
