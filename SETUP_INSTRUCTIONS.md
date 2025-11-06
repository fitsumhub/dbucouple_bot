# Python Installation Guide for Windows

## Step 1: Download Python

1. Go to **https://www.python.org/downloads/**
2. Click the big yellow "Download Python" button (latest version)
3. Run the downloaded installer (`.exe` file)

## Step 2: Install Python (IMPORTANT!)

During installation, **CHECK THIS BOX**:
- ✅ **"Add Python to PATH"** (at the bottom of the installer window)

Then click "Install Now"

## Step 3: Disable Windows App Execution Aliases

Windows 10/11 may interfere with Python. Fix this:

1. Press `Windows Key` + `I` to open Settings
2. Search for: **"Manage App Execution Aliases"**
3. Find these entries and turn them **OFF**:
   - `python.exe` → **OFF**
   - `python3.exe` → **OFF**

## Step 4: Verify Installation

**Close and reopen PowerShell**, then run:

```powershell
python --version
pip --version
```

You should see version numbers (not errors).

## Step 5: Install Bot Dependencies

```powershell
pip install -r requirements.txt
```

## Step 6: Run the Bot

```powershell
python bot.py
```

---

## Alternative: Use Microsoft Store

If you prefer, you can install Python from Microsoft Store:
1. Open Microsoft Store
2. Search for "Python 3.12" (or latest)
3. Click Install
4. Still need to disable App Execution Aliases (Step 3 above)

---

**Need help?** Make sure Python is added to PATH and App Execution Aliases are disabled!

