# AI SOC Simulator

A small local "SOC in a box" for learning how AI-assisted threat triage
works end to end:

```
log_generator.py  -->  detector.py  -->  ai_analyzer.py  -->  responder.py
  (synthetic          (cheap regex/         (LLM call:           (iptables /
   attack logs)         rate heuristics,    real threat vs        process isolate,
                         cuts API calls)     false positive)       forensic report)
                                                                        |
                                                                        v
                                                                    db.py (SQLite)
                                                                        |
                                                                        v
                                                               dashboard.py (Streamlit)
```

## What it actually does

- **Simulates attacks** — `log_generator.py` emits synthetic log lines shaped
  like brute-force SSH attempts, SQL injection HTTP requests, and malware C2
  beacon traffic, mixed in with benign traffic. No real network traffic is
  generated or sent anywhere.
- **Prefilters cheaply** — `detector.py` uses simple regex/rate-based rules
  (e.g. "5+ failed logins from one IP in 60s") so you're not paying for an
  LLM call on every log line, only the ones worth a second look.
- **AI triage** — `ai_analyzer.py` sends each flagged entry to the Anthropic
  API and asks for a structured verdict: real threat vs false positive, a
  confidence score, and a recommended action.
- **Automated response** — `responder.py` can block the attacker's IP via
  `iptables` and "isolate" a process. **Simulated by default** — see Safety
  below.
- **Dashboard** — `dashboard.py` is a live Streamlit view of events, verdicts,
  active blocks, and category breakdowns.

## Setup

```bash
cd ai_soc_simulator
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # get one at console.anthropic.com
```

## Run it

Terminal 1 — the pipeline:
```bash
python main.py
```

Terminal 2 — the dashboard:
```bash
streamlit run dashboard.py
```

Useful flags on `main.py`:
- `--events 100` — stop after 100 generated events instead of running forever
- `--fast` — shorten the interval between events for a quicker demo
- `--live` — see **Safety** below before using this

## Safety model — please read before using `--live`

By default (`config.LIVE_RESPONSE = False`, no `--live` flag), **nothing on
your real system is touched**. Every "block this IP" or "isolate this
process" action is logged with the exact command that *would* run, and
stored in the DB / forensic report as `mode: "simulated"`.

If you pass `--live`:
- IP blocking actually calls `iptables -A INPUT -s <ip> -j DROP`, which
  requires root and **modifies your real firewall rules**. Because the
  attacker IPs are synthetic/random, you could end up blocking real,
  unrelated addresses on your machine — only do this on a disposable VM or
  a machine where you're comfortable with that.
- Process isolation sends `SIGSTOP` (pause, not kill) to a real PID — but
  since this project's events are synthetic, there generally isn't a real
  PID to isolate, so this path mostly no-ops safely.

Recommended: run everything in simulate mode to learn the pipeline, and only
flip to `--live` inside an isolated VM or container if you specifically want
to test real firewall integration.

## Tuning

All thresholds live in `config.py` and are overridable via environment
variables — brute-force threshold/window, AI confidence cutoff, block
duration, generator speed, DB/report paths, and the model name (check
https://docs.claude.com for current model names before changing it).

## Files

| File | Purpose |
|---|---|
| `config.py` | All tunables, read from env vars |
| `log_generator.py` | Synthetic attack + benign log generation |
| `detector.py` | Cheap heuristic prefilter |
| `ai_analyzer.py` | Anthropic API call + JSON verdict parsing |
| `responder.py` | iptables block / process isolate / forensic report (simulate-first) |
| `db.py` | SQLite storage shared across processes |
| `main.py` | Orchestrator loop |
| `dashboard.py` | Streamlit live view |
