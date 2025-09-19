# LedgerLite Launcher Scripts

This directory contains several easy ways to launch LedgerLite without needing to remember complex commands or module paths.

## 🚀 Quick Start

### Option 1: Python Launcher (Recommended)
```bash
python run_ledgerlite.py
```

### Option 2: Shell Script (macOS/Linux)
```bash
./start_ledgerlite.sh
```

### Option 3: Batch File (Windows)
```cmd
start_ledgerlite.bat
```

### Option 4: Direct Module Launch
```bash
python -m ledgerlite.app.main
```

## 📋 What Each Launcher Does

### `run_ledgerlite.py`
- **Cross-platform** Python script
- Automatically sets up the Python path
- Provides helpful error messages and troubleshooting tips
- Handles import errors gracefully

### `start_ledgerlite.sh`
- **macOS/Linux** shell script
- Automatically activates virtual environment if present
- Installs package if not found
- Provides status messages during startup

### `start_ledgerlite.bat`
- **Windows** batch file
- Automatically activates virtual environment if present
- Installs package if not found
- Includes pause at end to see any error messages

## 🔧 Troubleshooting

### If you get import errors:
1. Make sure you're in the correct directory
2. Install dependencies: `pip install -e .`
3. Check that all required packages are installed

### If the application doesn't start:
1. Check that the database is properly initialized
2. Make sure all dependencies are installed
3. Try running the direct module command: `python -m ledgerlite.app.main`

### If you get permission errors (macOS/Linux):
```bash
chmod +x start_ledgerlite.sh
chmod +x run_ledgerlite.py
```

## 💡 Tips

- The **Python launcher** (`run_ledgerlite.py`) is the most reliable and provides the best error messages
- The **shell script** is great for daily use on macOS/Linux
- The **batch file** is perfect for Windows users
- All launchers will automatically handle virtual environment activation if present

## 🎯 Quick Commands

```bash
# Make launchers executable (macOS/Linux)
chmod +x *.py *.sh

# Run with Python launcher
python run_ledgerlite.py

# Run with shell script (macOS/Linux)
./start_ledgerlite.sh

# Run with batch file (Windows)
start_ledgerlite.bat
```

Choose the launcher that works best for your system and workflow! 🚀


