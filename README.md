# 🛡️ AI SOC Simulator

**An end-to-end AI-powered Security Operations Center (SOC) simulator** that demonstrates how modern threat detection works: synthetic attack generation → heuristic prefiltering → AI-driven triage → automated response.

Perfect for **learning**, **demos**, **education**, and **understanding SOC workflows**.

---

## 🎯 What It Does

```
┌─────────────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐
│   Synthetic │────→│  Heuristic│────→│ AI Triage │────→│Automated │
│  Log Gen    │     │ Prefilter │     │ (Claude)  │     │ Response │
└─────────────┘     └──────────┘     └───────────┘     └──────────┘
      ↓
   Generates:
   • Brute-force SSH attempts
   • SQL injection attacks
   • Malware C2 beacons
   • Benign traffic (mixed in)
   
   Flags:
   • 5+ failed logins/60s
   • SQL injection patterns
   • Suspicious outbound C2
   
   Decides:
   • Real threat or false positive?
   • Confidence score (0.0-1.0)
   • Recommended action
   
   Executes:
   • Block IP (iptables)
   • Isolate process (SIGSTOP)
   • Generate forensic report
   • Log to SQLite DB
   
   ↓
  Visualizes everything on live Streamlit dashboard
```

---

## ✨ Features

- **Synthetic Attack Generation** — Realistic logs without touching the network
- **Efficient Prefiltering** — Cheap regex/rate rules reduce API costs
- **AI Triage** — Claude AI makes context-aware threat/false-positive decisions
- **Mock Mode** — Run WITHOUT an API key using simulated verdicts (great for demos!)
- **Automated Response** — Block IPs, isolate processes, generate forensic reports
- **Live Dashboard** — Real-time Streamlit visualization
- **Safe by Default** — All responses are simulated; only apply real changes with `--live` flag

---

## 📊 Dashboard Output

The live dashboard shows:
- **Total events** processed
- **Flagged events** (caught by prefilter)
- **Confirmed threats** (AI verdict: real threat + high confidence)
- **False positives** (caught but not a real threat)
- **Active IP blocks** — currently blocked IPs with expiration times
- **Threat breakdown** — chart of threats by category (brute-force, SQL injection, C2)
- **Forensic reports** — links to incident details

---

## 🚀 Quick Start

### **Option 1: Run Without API Key (Mock Mode) — No setup required!**

```bash
cd ai_soc_simulator
pip install -r requirements.txt

# Terminal 1: Run the simulator
python main.py --events 100 --fast

# Terminal 2: Open dashboard
streamlit run dashboard.py
# → Open http://localhost:8501 in your browser
```

### **Option 2: Run With Claude API (Real AI Analysis)**

```bash
# Get API key from https://console.anthropic.com
export ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE

# Then run as above
python main.py --events 100 --fast
streamlit run dashboard.py
```

---

## 📋 Command-Line Flags

```bash
python main.py [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--events N` | Stop after N events instead of running forever |
| `--fast` | Use 0.3s interval between events (default: 1.5s) |
| `--live` | Actually run `iptables` and process isolation (be careful!) |

**Examples:**
```bash
python main.py                  # Run forever, 1.5s intervals, simulated responses
python main.py --events 50      # 50 events, then stop
python main.py --fast --events 100  # Quick demo: 100 events, 0.3s apart
python main.py --live --events 20   # Real firewall + process actions (needs root!)
```

---

## 🏗️ Architecture

| File | Purpose |
|------|---------|
| `main.py` | Orchestrator loop — coordinates the entire pipeline |
| `log_generator.py` | Emits synthetic attack and benign logs |
| `detector.py` | Cheap regex/rate-based prefilter (cuts API calls) |
| `ai_analyzer.py` | Sends flagged events to Claude API; handles mock mode |
| `responder.py` | Blocks IPs, isolates processes, generates forensic reports |
| `db.py` | SQLite storage (events, verdicts, blocks, reports) |
| `dashboard.py` | Streamlit live visualization |
| `config.py` | All configuration (env var overrides) |

---

## ⚙️ Configuration

All settings live in `config.py` and can be overridden via environment variables:

```bash
# Detection tuning
export SOC_BRUTE_FORCE_THRESHOLD=5              # Failed logins to flag
export SOC_BRUTE_FORCE_WINDOW=60                # Time window (seconds)
export SOC_AI_CONFIDENCE_THRESHOLD=0.7          # Min confidence to act

# Response behavior
export SOC_LIVE_RESPONSE=false                  # false = simulated (safe)
export SOC_BLOCK_DURATION=3600                  # How long to block IPs (seconds)

# Storage
export SOC_DB_PATH=./soc.db
export SOC_FORENSICS_DIR=./forensic_reports

# Generation
export SOC_GEN_INTERVAL=1.5                     # Seconds between events
export SOC_AI_MODEL=claude-sonnet-4-6           # Model name (update as needed)
```

---

## 🔒 Safety Model — Please Read

### **Default Mode (Safe)**
- `config.LIVE_RESPONSE = False` (no `--live` flag)
- **Nothing touches your real system**
- All "block IP" or "isolate process" actions are **logged and simulated**
- Perfect for learning and demos

### **Live Mode (`--live` flag)**
- **IP blocking** calls `iptables -A INPUT -s <ip> -j DROP` (requires `root`)
- **Process isolation** sends `SIGSTOP` to a real PID
- **⚠️ Use only on disposable VMs** — synthetic attacker IPs might collide with real addresses
- Real firewall integration testing only

---

## 📈 Use Cases

- **Security education** — Learn how SOCs detect and respond to threats
- **Live demos** — Show how AI triage works to teams/customers
- **Testing workflows** — Validate incident response playbooks
- **Benchmarking** — Test detection thresholds and tuning
- **Prototyping** — Experiment with new threat classifiers before production

---

## 🔧 Example Outputs

### **Console Output (main.py)**
```
[INFO] Running in MOCK mode (no API key) — using simulated threat verdicts
=== AI SOC Simulator starting — response mode: SIMULATED (safe, no system changes) ===
DB: ./soc.db
Model: claude-sonnet-4-6

[benign] brute_force    131.161.28.137  sshd[1350]: Failed password for backup...
[FLAGGED] malware_c2    59.197.51.203   [25/Sep/2026:11:39:22 +0000] conn: local_process=python3...
    -> AI: REAL THREAT (malware_c2, conf=0.85) -> action=isolate_process
    -> response: Simulated isolation of process_name=malware_c2
    -> forensic report: ./forensic_reports/incident_20260925T113922_59-197-51-203.json
```

### **Forensic Report (JSON)**
```json
{
  "incident_id": "incident_20260925T113922_59-197-51-203",
  "timestamp": "2026-09-25T11:39:22.123456Z",
  "event": {
    "category": "malware_c2",
    "source_ip": "59.197.51.203",
    "raw_log": "[25/Sep/2026:11:39:22] conn: local_process=python3 pid=11330 src=59.197.51.203 dst=threat.example.com:443"
  },
  "ai_verdict": {
    "verdict": "real_threat",
    "confidence": 0.85,
    "threat_type": "malware_c2",
    "reasoning": "Suspicious outbound connection pattern consistent with C2 beacon activity.",
    "recommended_action": "isolate_process"
  },
  "response": {
    "action": "isolate_process",
    "mode": "simulated",
    "detail": "Simulated isolation of process_name=malware_c2"
  }
}
```

---

## 🌐 Deploy as a Web Platform

This project can be deployed as a hosted demo or educational platform:

### **Option A: Docker Container (Simple)**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY ai_soc_simulator /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "dashboard.py"]
```

### **Option B: Docker Compose (Full Stack)**
```yaml
version: '3.8'
services:
  simulator:
    build: .
    command: python main.py --fast
  dashboard:
    build: .
    ports:
      - "8501:8501"
    command: streamlit run dashboard.py
```

### **Option C: Heroku / Cloud Platform**
See deployment guide in docs/DEPLOYMENT.md (coming soon).

---

## 📦 Requirements

- Python 3.10+
- `anthropic` >= 0.40.0 (for real API mode)
- `streamlit` >= 1.38.0
- `pandas` >= 2.0.0

Install:
```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing

Found a bug? Want to add a new attack type or detection rule? PRs welcome!

---

## 📄 License

[Choose: MIT, Apache 2.0, GPL, etc.]

---

## 🎓 Learn More

- [Anthropic Claude Docs](https://docs.claude.com)
- [Streamlit Docs](https://docs.streamlit.io)
- [SOC Best Practices](https://www.siem.com) (example resource)

---

## 📞 Questions?

- Read the README in `ai_soc_simulator/`
- Check `config.py` for all tunable parameters
- Review forensic reports in `forensic_reports/` directory
- Open an issue on GitHub!

---

**Built with ❤️ for security education and demos**
