# 🎯 Easy Setup for Normal Users (No Terminal Knowledge Needed!)

## **For Windows Users - The Simplest Way**

### **Step 1: Download & Extract**

1. Go to: https://github.com/manashbajpai8840-alt/ai-soc-simulator
2. Click **"Code"** → **"Download ZIP"**
3. Extract the ZIP file to your computer (anywhere is fine)
   - Right-click ZIP → **"Extract All"** → Choose folder

**Your folder should look like:**
```
ai-soc-simulator/
├── START_SIMULATOR.bat          ← Double-click this!
├── START_DASHBOARD.bat          ← Or this!
├── ai_soc_simulator/
│   ├── dashboard.py
│   ├── main.py
│   └── ... (other files)
└── README.md
```

---

### **Step 2: Install Python (One-time only)**

1. Go to: https://www.python.org/downloads/
2. Click **"Download Python 3.11"** (or latest)
3. Run the installer
4. **IMPORTANT:** Check the box: ✅ **"Add Python to PATH"**
5. Click **"Install Now"**

**Done!** Python is installed. You only need to do this once.

---

### **Step 3: Choose Your Option**

#### **Option A: See Live Data (Recommended for First Time)**

1. **Double-click: `START_SIMULATOR.bat`**
   - A black window appears
   - Shows threats being detected
   - Runs for ~30 seconds
   - Press any key when done

**Output looks like:**
```
[FLAGGED] brute_force 141.238.76.79 sshd[7913]: Failed password...
    -> AI: REAL THREAT (brute_force, conf=0.77) -> action=block_ip
    -> response: Simulated only — no firewall rule was actually applied.
```

---

#### **Option B: See Beautiful Dashboard**

1. **Double-click: `START_DASHBOARD.bat`**
   - Your browser opens
   - Shows pretty charts and tables
   - Updates in real-time
   - Keep it running

**You see:**
- Total events counter
- Threats chart
- Blocked IPs table
- All threat details

---

#### **Option C: Run Both Together (Like a Pro)**

**Terminal 1:**
1. Double-click `START_SIMULATOR.bat`
   - Shows threats being detected
   - Keep this running

**Terminal 2:**
1. Double-click `START_DASHBOARD.bat`
   - Shows beautiful visualization
   - Updates as Terminal 1 runs

---

## **🎨 Make It Easier - Desktop Shortcuts**

### **Create a Desktop Shortcut (Windows)**

1. Right-click on `START_SIMULATOR.bat`
2. Click **"Create Shortcut"**
3. Drag the shortcut to your **Desktop**
4. Double-click anytime!

**Optional: Change icon**
1. Right-click shortcut → **"Properties"**
2. Click **"Change Icon"**
3. Pick a cool icon
4. Click **"OK"**

---

## **🔄 Make It Run Automatically (Startup)**

### **Option 1: Start When Computer Boots**

1. Press **Windows + R**
2. Type: `shell:startup`
3. Press **Enter**
4. Copy `START_SIMULATOR.bat` into this folder

**Now it runs every time you restart your computer!**

---

### **Option 2: Scheduled Task (Windows)**

1. Press **Windows Key**
2. Search: **"Task Scheduler"**
3. Click **"Create Basic Task"**
4. Fill in:
   - **Name:** AI SOC Simulator
   - **Trigger:** When I log in
   - **Action:** Start a program
   - **Program:** `START_SIMULATOR.bat`
5. Click **"Finish"**

**Now it runs automatically when you log in!**

---

## **💻 Share with Others - How They Use It**

### **For a Friend/Colleague**

1. Send them the GitHub link: https://github.com/manashbajpai8840-alt/ai-soc-simulator
2. They download and extract ZIP
3. They double-click `START_SIMULATOR.bat` or `START_DASHBOARD.bat`
4. They see it working immediately!

**No terminal knowledge needed!**

---

## **🌐 Make It a Website (Advanced but Easy)**

If you want to share WITHOUT asking people to download:

### **Option 1: Host on Streamlit Cloud (Free!)**

We already deployed it here:
```
https://ai-soc-simulator-hsxzyjprvmro6fq4m4brlf.streamlit.app
```

Anyone can visit this URL and see the dashboard live!

**How to share:**
- Send the link to friends
- Post on social media
- Add to your portfolio
- People click the link, see it working

---

### **Option 2: Create a Simple Windows Installer**

Want a professional `.exe` installer?

I can create one so people just:
1. Download `AI-SOC-Simulator-Setup.exe`
2. Click it
3. Choose install location
4. It's installed!
5. Desktop shortcut created automatically

Would you like me to create this?

---

## **📱 Mobile Access (View on Phone)**

If both laptop and phone are on same WiFi:

1. Run `START_DASHBOARD.bat` on your laptop
2. Note the IP address from terminal output (e.g., `192.168.1.100`)
3. On your phone, visit: `http://192.168.1.100:8501`
4. See dashboard on your phone!

---

## **🎯 Quick Reference - 3 Ways to Use**

### **Way 1: Just See It Work (Easiest)**
```
1. Double-click START_SIMULATOR.bat
2. Watch threats appear
3. Press any key to close
```
**Time: 2 minutes** ⏱️

---

### **Way 2: See Beautiful Dashboard**
```
1. Double-click START_DASHBOARD.bat
2. Browser opens automatically
3. Click "Run Simulator" link or run START_SIMULATOR.bat separately
4. Watch dashboard update
```
**Time: 5 minutes** ⏱️

---

### **Way 3: Share as Website**
```
1. Send this link: https://ai-soc-simulator-hsxzyjprvmro6fq4m4brlf.streamlit.app
2. Friend clicks link
3. They see live dashboard
4. Your laptop must be running START_SIMULATOR.bat
```
**Time: 0 minutes (they just click!)** ⏱️

---

## **🆘 Troubleshooting**

### **"Python not found"**
- Download Python: https://www.python.org/downloads/
- **Don't forget:** Check ✅ "Add Python to PATH"
- Restart your computer
- Try again

---

### **"Port 8501 already in use"**
- Another app is using it
- Close browser and try again
- Or edit `START_DASHBOARD.bat`:
  ```bat
  streamlit run dashboard.py --server.port 8502
  ```

---

### **"Nothing happens when I double-click"**
- Check if a window opened and closed quickly
- Try: Right-click → "Run as Administrator"

---

## **✅ Checklist**

- ✅ Downloaded and extracted ZIP
- ✅ Installed Python with "Add to PATH"
- ✅ Double-clicked `START_SIMULATOR.bat` — it works!
- ✅ Double-clicked `START_DASHBOARD.bat` — browser opened!
- ✅ Created desktop shortcut for easy access
- ✅ (Optional) Added to startup folder

---

**You're Done! 🎉**

Now you can:
- ✅ Run it anytime by double-clicking
- ✅ Share with anyone (just send GitHub link)
- ✅ Host it online for others to access
- ✅ Show it as a working demo

**Enjoy your AI SOC Simulator! 🚀**
