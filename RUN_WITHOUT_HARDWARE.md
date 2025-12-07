# Step-by-Step Guide to Run Without Hardware

## Prerequisites
- Python 3.9+ installed
- PowerShell terminal

## Step 1: Create Virtual Environment
```powershell
python -m venv venv
```

## Step 2: Install Dependencies
Since PowerShell script execution may be disabled, use the Python executable directly:

```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Step 3: Run Mock Demo (No Hardware Needed)
```powershell
.\venv\Scripts\python.exe mock_demo.py
```

This will:
- Create virtual temperature, humidity, and pressure sensors
- Generate random readings every 2 seconds
- Validate the data
- Display formatted telemetry messages
- Show the complete system working without any hardware

**Press Ctrl+C to stop the demo**

## Step 4: Run Unit Tests
```powershell
.\venv\Scripts\python.exe -m pytest
```

This will:
- Run all unit tests
- Show test results
- Display code coverage

## Step 5: Run Tests with Coverage Report
```powershell
.\venv\Scripts\python.exe -m pytest --cov=src --cov-report=html
```

Then open the coverage report:
```powershell
.\htmlcov\index.html
```

## Alternative: Enable PowerShell Scripts (Optional)

If you want to use the activation scripts, run PowerShell as Administrator:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then you can activate the virtual environment normally:
```powershell
.\venv\Scripts\Activate.ps1
python mock_demo.py
pytest
```

## Quick Commands Summary

**Without activating venv:**
```powershell
# Run mock demo
.\venv\Scripts\python.exe mock_demo.py

# Run tests
.\venv\Scripts\python.exe -m pytest

# Run with coverage
.\venv\Scripts\python.exe -m pytest --cov=src
```

**With activated venv:**
```powershell
# Activate (if execution policy allows)
.\venv\Scripts\Activate.ps1

# Then simply run:
python mock_demo.py
pytest
```

## Expected Output from Mock Demo

```
=== IoT Edge Device Mock Demo ===

{"timestamp": "2025-12-07T...", "level": "INFO", ...}
Connected mock sensor: temperature_sensor
Connected mock sensor: humidity_sensor
Connected mock sensor: pressure_sensor

Reading sensors every 2 seconds. Press Ctrl+C to stop.

[10:30:45] Telemetry Message:
  ✓ temperature_sensor: 25.34 celsius
  ✓ humidity_sensor: 55.21 percent
  ✓ pressure_sensor: 1013.45 hPa

[10:30:47] Telemetry Message:
  ✓ temperature_sensor: 26.12 celsius
  ✓ humidity_sensor: 58.93 percent
  ✓ pressure_sensor: 1015.22 hPa
```

## Troubleshooting

**"python: command not found"**
- Try `py` instead of `python`
- Or use full path: `C:\Python312\python.exe`

**"Module not found" errors**
- Make sure you installed dependencies: `.\venv\Scripts\python.exe -m pip install -r requirements.txt`

**"Permission denied"**
- Run PowerShell as Administrator
- Or use the `.\venv\Scripts\python.exe` commands shown above
