# 🎯 How to Use the AI SOC Simulator

A complete guide to running, understanding, and using the AI SOC Simulator.

---

## 🚀 Quick Start (30 seconds)

### **Terminal 1: Run the Simulator**
```powershell
cd ai_soc_simulator
python main.py --events 50 --fast
```

### **Terminal 2: Open the Dashboard**
```powershell
cd ai_soc_simulator
streamlit run dashboard.py
```

Then visit: **http://localhost:8501**

That's it! Watch the dashboard populate in real-time. ✅

---

## 📊 Understanding the Dashboard

### **Top Metrics**

| Metric | What It Means |
|--------|---------------|
| **Total events** | Every log line (attack + benign) |
| **Flagged by prefilter** | Suspicious logs caught by cheap rules |
| **Confirmed threats** | AI verdict = "real threat" + high confidence |
| **False positives** | Flagged by rules but AI says "benign" |
| **Active IP blocks** | Attacker IPs currently blocked |

**Example Reading:**
```
380 total events
├─ 46 flagged (suspicious patterns detected)
├─ 30 confirmed threats (AI agrees, high confidence)
├─ 6 false positives (rules flagged, but AI says safe)
└─ 7 active IP blocks (these attackers are blocked)
```

---

### **Threats by Category Chart**

Shows breakdown of threat types:

- **brute_force** — Failed login attempts (SSH, FTP)
  - Rule: 5+ failed logins from one IP in 60 seconds
  
- **malware_c2** — Suspicious outbound connections (Command & Control)
  - Rule: Patterns like suspicious DNS queries, C2 beacon traffic
  
- **sql_injection** — SQL injection attempts in HTTP requests
  - Rule: Detects SQL patterns like `' OR '1'='1`, `admin'--`, etc.

---

### **Active IP Blocks Table**

Shows which attacker IPs are currently blocked:

| Column | Meaning |
|--------|---------|
| **ip** | Attacker's IP address |
| **blocked_at** | When the block was applied |
| **expires_at** | When the block expires (config: 1 hour default) |
| **mode** | "simulated" = safe test mode, "live" = real firewall |

**Example:**
```
IP: 49.21.190.186
Blocked at: 1790335629.5709
Expires at: 1790339229.5709
Mode: simulated ← No real firewall change (safe!)
```

---

### **Recent Events Table**

Shows the latest log entries and their analysis:

| Column | Meaning |
|--------|---------|
| **ts** | Timestamp |
| **category** | brute_force / malware_c2 / sql_injection / benign |
| **source_ip** | Attacker's IP |
| **prefilter_flagged** | 1 = flagged, 0 = benign |
| **ai_verdict** | "real_threat" / "false_positive" / "None" |
| **ai_confidence** | 0.0 to 1.0 (how sure the AI is) |
| **response_action** | block_ip / isolate_process / monitor / none |
| **raw_log** | Full log line |

---

## 🎮 Command-Line Options

### **Basic Run**
```powershell
python main.py
```
- Runs **forever** until you press Ctrl+C
- 1.5 second interval between events
- All responses **simulated** (safe)

---

### **Quick Demo (Recommended)**
```powershell
python main.py --events 50 --fast
```
- Stops after **50 events**
- **0.3 second** intervals (super fast!)
- Perfect for seeing it in action quickly

---

### **Longer Demo**
```powershell
python main.py --events 200 --fast
```
- 200 events
- Fast interval
- Takes ~60 seconds

---

### **Slow & Steady**
```powershell
python main.py --events 100
```
- 100 events
- 1.5 second interval (normal speed)
- Easy to follow what's happening

---

### **Live Mode (⚠️ Be Careful!)**
```powershell
python main.py --events 50 --live
```
- ⚠️ **REAL firewall changes** (requires root/admin)
- Actually calls `iptables` on Linux/Mac
- Synthetic IPs might collide with real addresses
- **Only use on a test VM!**

---

## 🔍 Console Output - Reading it

When you run `python main.py`, you'll see output like:

```
=== AI SOC Simulator starting — response mode: SIMULATED (safe, no system changes) ===
DB: soc.db
Model: claude-sonnet-4-6

[benign] brute_force    131.161.28.137  sshd[1350]: Failed password for backup...
[benign] benign         192.168.1.236   192.168.1.236 - - [25/Sep/2026:11:39:19]...
[FLAGGED] malware_c2    59.197.51.203   [25/Sep/2026:11:39:22] conn: local_process...
    -> AI: REAL THREAT (malware_c2, conf=0.85) -> action=isolate_process
    -> response: Simulated isolation of process_name=malware_c2
    -> forensic report: ./forensic_reports/incident_20260925T113922_59-197-51-203.json
```

### **Reading Each Line:**

**`[benign] brute_force 131.161.28.137 ...`**
- `[benign]` = Prefilter caught it, but doesn't meet threshold
- `brute_force` = Attack category
- `131.161.28.137` = Source IP
- Rest = Log content

**`[FLAGGED] malware_c2 59.197.51.203 ...`**
- `[FLAGGED]` = Prefilter thinks it's suspicious
- Sending to AI for analysis...

**`-> AI: REAL THREAT (malware_c2, conf=0.85) -> action=isolate_process`**
- AI verdict: **Real threat** (not false positive)
- Confidence: **0.85** (85% sure)
- Threat type: **malware_c2**
- Recommended: **isolate_process**

**`-> response: Simulated isolation...`**
- Action was **simulated** (safe, nothing actually happened)

**`-> forensic report: ./forensic_reports/incident_...json`**
- Detailed report saved to JSON file

---

## 📁 What Gets Created/Updated

### **SQLite Database: `soc.db`**
Stores all events, verdicts, blocks, and reports. Updates live as events happen.

**Access it:**
```powershell
# View all events
sqlite3 soc.db "SELECT * FROM events LIMIT 10;"

# View threats only
sqlite3 soc.db "SELECT * FROM events WHERE category='malware_c2';"

# View blocked IPs
sqlite3 soc.db "SELECT * FROM blocked_ips;"
```

---

### **Forensic Reports: `forensic_reports/`**
One JSON file per confirmed threat.

**Example: `incident_20260925T113922_59-197-51-203.json`**
```json
{
  "incident_id": "incident_20260925T113922_59-197-51-203",
  "timestamp": "2026-09-25T11:39:22Z",
  "event": {
    "category": "malware_c2",
    "source_ip": "59.197.51.203",
    "raw_log": "[25/Sep/2026:11:39:22] conn: local_process=python3..."
  },
  "ai_verdict": {
    "verdict": "real_threat",
    "confidence": 0.85,
    "threat_type": "malware_c2",
    "reasoning": "Suspicious outbound connection pattern consistent with C2 beacon...",
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

## ⚙️ Configuration - Tuning the Simulator

Edit `config.py` or set environment variables:

### **Detection Sensitivity**

```powershell
# How many failed logins to flag as brute-force
export SOC_BRUTE_FORCE_THRESHOLD=5

# Time window for counting failed logins (seconds)
export SOC_BRUTE_FORCE_WINDOW=60
```

**Example:** 5 failed logins within 60 seconds = flagged

---

### **AI Confidence Threshold**

```powershell
# Minimum confidence to act (0.0 to 1.0)
export SOC_AI_CONFIDENCE_THRESHOLD=0.7
```

**Example:** If AI is only 60% sure, it won't block. If 80% sure, it will.

---

### **Response Behavior**

```powershell
# false = simulated (safe), true = real changes
export SOC_LIVE_RESPONSE=false

# How long to block an IP (seconds)
export SOC_BLOCK_DURATION=3600  # 1 hour
```

---

### **Event Generation Speed**

```powershell
# Seconds between events
export SOC_GEN_INTERVAL=1.5

# Or use --fast flag:
python main.py --fast  # 0.3 second interval
```

---

## 🎓 Learning Scenarios

### **Scenario 1: Quick Demo (5 minutes)**
```powershell
python main.py --events 30 --fast
streamlit run dashboard.py
# Watch: Threats appear, IPs get blocked in real-time
```

---

### **Scenario 2: Understand Detection Rules**
```powershell
python main.py --events 100
# Watch the console
# Count: How many "benign" vs "[FLAGGED]"?
# Notice: Patterns of when rules trigger
```

---

### **Scenario 3: Study AI Verdicts**
```powershell
python main.py --events 50
# Look at each "[FLAGGED]" event
# Read the AI reasoning
# Observe confidence scores
# See false positives (flagged but not threats)
```

---

### **Scenario 4: Investigate Incidents**
```powershell
# Find forensic report
cd forensic_reports
# Open any .json file
# Read: What was detected, why, what action was taken
```

---

## 🔐 Safety - What Actually Happens?

### **Default Mode (Safe)**
```
Prefilter catches suspicious pattern
    ↓
AI says "real threat" + high confidence
    ↓
Simulator LOGS the action but doesn't execute
    ↓
Report says: mode=simulated (no real changes)
```

**Result:** Nothing happens to your system. Perfect for learning!

---

### **With --live Flag (⚠️ Dangerous)**
```
Prefilter catches suspicious pattern
    ↓
AI says "real threat"
    ↓
Simulator ACTUALLY RUNS:
  - iptables -A INPUT -s <ip> -j DROP  (blocks IP in firewall!)
  - kill -STOP <pid>  (pauses a real process!)
```

**Result:** Real firewall changes. Use only on test VMs!

---

## 📈 Typical Workflow

### **Step 1: Start Dashboard**
```powershell
# Terminal 2
streamlit run dashboard.py
# Opens http://localhost:8501
```

### **Step 2: Run Simulator**
```powershell
# Terminal 1
python main.py --events 100 --fast
```

### **Step 3: Watch in Real-Time**
- Console shows each event being processed
- Dashboard updates with metrics, charts, tables
- As threats are detected, you see:
  - Confirmed threats counter ⬆️
  - Active IP blocks table updates
  - Chart shows threat distribution

### **Step 4: Review Forensics**
- Check `forensic_reports/` folder
- Open JSON files
- See detailed incident analysis

---

## 🐛 Troubleshooting

### **"No events showing in dashboard"**
- Make sure `python main.py` is running in another terminal
- Check if `soc.db` exists in the same folder
- Try: `python main.py --events 10 --fast` (test mode)

### **"Port 8501 already in use"**
```powershell
streamlit run dashboard.py --server.port 8502
# Or stop the other Streamlit process
```

### **"No threats detected"**
- The simulator randomly generates events
- Some runs have fewer threats
- Try `--events 200 --fast` for more data
- Or manually tune detection rules in `config.py`

### **"Database locked"**
- Only run one simulator at a time
- Or delete `soc.db` and restart

---

## 🎯 Tips & Tricks

✅ **Watch the console** — You see everything being processed
✅ **Dashboard = summary** — Console = detailed logs
✅ **Forensic reports are gold** — Full incident details
✅ **Try different thresholds** — Tune config.py to see impact
✅ **Run multiple times** — Different threats each run (randomized)
✅ **Share screenshots** — Great portfolio evidence!

---

## 📚 Next Steps

1. **Run it yourself** — Get hands-on
2. **Tweak config.py** — Change thresholds, see impact
3. **Add custom attack types** — Extend log_generator.py
4. **Share on GitHub** — You already did! ✅
5. **Record a demo** — Impress your friends/team

---

**Happy simulating! 🚀**
