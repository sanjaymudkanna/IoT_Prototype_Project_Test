# Git Setup and Push to Private Repository - Step by Step Guide

## Step 1: Initialize Git Repository

```powershell
git init
```

## Step 2: Configure Git (First Time Only)

If you haven't configured Git before on this machine:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 3: Add All Files to Git

```powershell
git add .
```

## Step 4: Create Initial Commit

```powershell
git commit -m "Initial commit: Production-ready IoT Edge Device project"
```

## Step 5: Create Private Repository on GitHub

### Option A: Using GitHub Web Interface
1. Go to https://github.com
2. Click the **+** icon (top right) → **New repository**
3. Enter repository name: `iot-edge-device` (or your preferred name)
4. Select **Private** 
5. Do NOT initialize with README (we already have one)
6. Click **Create repository**

### Option B: Using GitHub CLI (if installed)
```powershell
gh repo create iot-edge-device --private --source=. --remote=origin
```

## Step 6: Add Remote Repository

Copy the repository URL from GitHub (looks like `https://github.com/yourusername/iot-edge-device.git`)

```powershell
git remote add origin https://github.com/yourusername/iot-edge-device.git
```

## Step 7: Push to GitHub

```powershell
git branch -M main
git push -u origin main
```

## Complete Command Sequence

```powershell
# Initialize and commit
git init
git add .
git commit -m "Initial commit: Production-ready IoT Edge Device project"

# Add remote (replace with your actual repository URL)
git remote add origin https://github.com/yourusername/iot-edge-device.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Authentication Options

### Option 1: Personal Access Token (Recommended)
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click **Generate new token (classic)**
3. Give it a name: "IoT Edge Device"
4. Select scopes: **repo** (full control of private repositories)
5. Click **Generate token**
6. **Copy the token** (you won't see it again!)
7. When pushing, use token as password:
   - Username: your GitHub username
   - Password: paste the token

### Option 2: SSH Key
```powershell
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your.email@example.com"

# Copy public key
Get-Content ~\.ssh\id_ed25519.pub | Set-Clipboard

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
# Then use SSH URL: git@github.com:yourusername/iot-edge-device.git
```

## What Gets Pushed (What's NOT Ignored)

✅ Source code (`src/`)
✅ Tests (`tests/`)
✅ Configuration files (`config.yaml`, `requirements.txt`)
✅ Documentation (`README.md`, `QUICKSTART.md`, etc.)
✅ Docker and setup files

❌ Virtual environment (`venv/`) - excluded by `.gitignore`
❌ Log files (`logs/`) - excluded by `.gitignore`
❌ Python cache (`__pycache__/`) - excluded by `.gitignore`
❌ Test coverage reports (`htmlcov/`, `.coverage`)

## Future Updates

After making changes, use:

```powershell
# Check status
git status

# Add changed files
git add .

# Or add specific files
git add src/main.py

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push
```

## Verify Upload

After pushing, visit your repository on GitHub:
```
https://github.com/yourusername/iot-edge-device
```

You should see all your project files there!

## Clone on Another Machine

To download this project on another computer:

```powershell
git clone https://github.com/yourusername/iot-edge-device.git
cd iot-edge-device
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Troubleshooting

**"fatal: not a git repository"**
→ Run `git init` first

**"remote origin already exists"**
→ Run `git remote remove origin` then add again

**"Authentication failed"**
→ Use Personal Access Token instead of password
→ Or set up SSH keys

**"Updates were rejected"**
→ Pull first: `git pull origin main --rebase`
→ Then push: `git push`

**Want to check remote URL?**
```powershell
git remote -v
```
