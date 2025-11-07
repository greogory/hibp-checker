# Installing HIBP Checker on Windows

---

## ⚡ Powered by Have I Been Pwned

This tool uses data from **[Have I Been Pwned](https://haveibeenpwned.com)** by Troy Hunt, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

**Prerequisites**: Requires a **[Have I Been Pwned API subscription](https://haveibeenpwned.com/API/Key)** (Pwned 1-4 tier). See [HIBP API documentation](https://haveibeenpwned.com/API/v3) for details.

**Support HIBP**: Consider [subscribing](https://haveibeenpwned.com/API/Key) or [donating](https://haveibeenpwned.com/Donate) to help maintain this critical security service.

---

This guide provides detailed instructions for running the HIBP Comprehensive Breach Checker on Windows using either WSL2 (recommended) or Docker.

## Table of Contents

- [Option 1: WSL2 (Recommended)](#option-1-wsl2-recommended)
- [Option 2: Docker](#option-2-docker)
- [Troubleshooting](#troubleshooting)

---

## Option 1: WSL2 (Recommended)

WSL2 (Windows Subsystem for Linux 2) provides a complete Linux environment on Windows, making it the best option for running bash scripts.

### Prerequisites

- Windows 10 version 2004+ (Build 19041+) or Windows 11
- Administrator access

### Step 1: Install WSL2

1. **Open PowerShell as Administrator** and run:

```powershell
wsl --install
```

This installs WSL2 with Ubuntu by default.

2. **Restart your computer** when prompted.

3. **Set up your Linux username and password** when Ubuntu launches for the first time.

### Step 2: Update Ubuntu

Once inside Ubuntu (WSL2), update the system:

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 3: Install Dependencies

Install Python 3 and pip:

```bash
sudo apt install python3 python3-pip git -y
```

Verify installation:

```bash
python3 --version
pip3 --version
```

### Step 4: Install HIBP Checker

```bash
# Clone the repository
git clone https://github.com/greogory/hibp-checker.git
cd hibp-checker

# Make scripts executable
chmod +x hibp_workflow.sh
chmod +x hibp_comprehensive_checker.py
chmod +x quick_start.sh
chmod +x multi_email_setup.sh

# Install Python dependencies
pip3 install requests
```

### Step 5: Configure API Key

**Method 1 (Recommended): Environment Variable**

Add to your `~/.bashrc`:

```bash
echo 'export HIBP_API_KEY="your-32-character-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

Verify it's set:
```bash
echo $HIBP_API_KEY
```

**Method 2 (Alternative): Config File**

```bash
# Copy example config
cp hibp_config.conf.example hibp_config.conf

# Edit configuration with nano
nano hibp_config.conf
```

Add your HIBP API key to the `HIBP_API_KEY=""` line. Press `Ctrl+X`, then `Y`, then `Enter` to save in nano.

> **Security Note**: Environment variables are recommended as they're more secure than storing keys in config files.

### Step 6: Create Email List

```bash
# Copy template
cp my_emails_template.txt my_emails.txt

# Edit email list
nano my_emails.txt
```

Add your email addresses (one per line), save and exit.

### Step 7: Run Your First Check

```bash
# Interactive setup (optional)
./quick_start.sh

# Or run directly
./hibp_workflow.sh check
```

### Accessing Files from Windows

Your WSL2 files can be accessed from Windows File Explorer at:

```
\\wsl$\Ubuntu\home\YOUR_USERNAME\hibp-checker
```

You can also access Windows files from WSL2 at `/mnt/c/` (your C: drive).

### Tips for WSL2

**Opening WSL2 Terminal:**
- Search for "Ubuntu" in Windows Start Menu
- Or run `wsl` from PowerShell/Command Prompt

**Running commands from Windows:**
```powershell
# Run from PowerShell
wsl bash -c "cd ~/hibp-checker && ./hibp_workflow.sh check"
```

**Scheduling with Windows Task Scheduler:**
Create a task that runs:
```powershell
wsl bash -c "cd ~/hibp-checker && ./hibp_workflow.sh check > ~/hibp-logs/$(date +%Y%m%d).log 2>&1"
```

---

## Option 2: Docker

Docker provides an isolated environment and works on any Windows version that supports Docker.

### Prerequisites

- Windows 10/11 Pro, Enterprise, or Education (for Docker Desktop with Hyper-V)
- OR Windows 10/11 Home with WSL2 backend

### Step 1: Install Docker Desktop

1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Install and restart your computer
3. Start Docker Desktop

### Step 2: Create Project Directory

Create a directory for the project on your Windows machine:

```powershell
# In PowerShell
mkdir C:\hibp-checker
cd C:\hibp-checker
```

### Step 3: Download Files

Download the repository files:

```powershell
# Option A: Use git (if installed)
git clone https://github.com/greogory/hibp-checker.git .

# Option B: Download ZIP from GitHub
# Go to https://github.com/greogory/hibp-checker
# Click "Code" > "Download ZIP"
# Extract to C:\hibp-checker
```

### Step 4: Create Dockerfile

Create a file named `Dockerfile` in `C:\hibp-checker\`:

```dockerfile
FROM python:3.9-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y bash && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy all files
COPY . /app/

# Make scripts executable
RUN chmod +x *.sh *.py

# Install Python dependencies
RUN pip3 install --no-cache-dir requests

# Default command
CMD ["bash"]
```

### Step 5: Create Docker Compose File (Optional but Recommended)

Create `docker-compose.yml` in `C:\hibp-checker\`:

```yaml
version: '3.8'

services:
  hibp-checker:
    build: .
    container_name: hibp-checker
    volumes:
      - ./hibp_config.conf:/app/hibp_config.conf
      - ./my_emails.txt:/app/my_emails.txt
      - ./reports:/app/reports
      - ./logs:/app/logs
    working_dir: /app
    stdin_open: true
    tty: true
```

### Step 6: Configure

```powershell
# Copy example config
copy hibp_config.conf.example hibp_config.conf

# Edit with notepad
notepad hibp_config.conf
```

Add your API key and save.

```powershell
# Copy email template
copy my_emails_template.txt my_emails.txt

# Edit email list
notepad my_emails.txt
```

### Step 7: Build Docker Image

```powershell
docker build -t hibp-checker .
```

### Step 8: Run with Docker

**Option A: Using docker-compose (Recommended)**

```powershell
# Run interactively
docker-compose run --rm hibp-checker bash

# Inside container, run:
./hibp_workflow.sh check
```

**Option B: Using docker run**

```powershell
# Run a check
docker run --rm `
  -v ${PWD}/hibp_config.conf:/app/hibp_config.conf `
  -v ${PWD}/my_emails.txt:/app/my_emails.txt `
  -v ${PWD}/reports:/app/reports `
  hibp-checker `
  ./hibp_workflow.sh check
```

**Option C: Run Python script directly**

```powershell
docker run --rm `
  -v ${PWD}/hibp_config.conf:/app/hibp_config.conf `
  -v ${PWD}/my_emails.txt:/app/my_emails.txt `
  -v ${PWD}/reports:/app/reports `
  hibp-checker `
  python3 /app/hibp_comprehensive_checker.py `
  -k YOUR_API_KEY `
  --email-file /app/my_emails.txt `
  -o text -v
```

### Step 9: Access Reports

Reports will be saved to `C:\hibp-checker\reports\` and can be opened with any text editor.

### Docker Tips

**View logs:**
```powershell
docker-compose logs
```

**Access container shell:**
```powershell
docker-compose run --rm hibp-checker bash
```

**Remove containers and images:**
```powershell
docker-compose down
docker rmi hibp-checker
```

**Schedule checks with Windows Task Scheduler:**

Create a batch file `run-hibp-check.bat`:
```batch
@echo off
cd C:\hibp-checker
docker-compose run --rm hibp-checker ./hibp_workflow.sh check > logs\%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1
```

Then create a scheduled task to run this batch file.

---

## Troubleshooting

### WSL2 Issues

**"WSL 2 requires an update to its kernel component"**
- Download and install the WSL2 kernel update: https://aka.ms/wsl2kernel

**"The requested operation requires elevation"**
- Run PowerShell as Administrator

**Can't find Ubuntu after install:**
- Open Microsoft Store and search for "Ubuntu"
- Install "Ubuntu 22.04 LTS" or "Ubuntu"

**Python command not found:**
```bash
# Update package list
sudo apt update

# Install python3
sudo apt install python3 python3-pip -y
```

**Permission denied on scripts:**
```bash
# Make scripts executable
chmod +x *.sh *.py
```

### Docker Issues

**"Docker Desktop requires Windows 10 Pro"**
- Enable WSL2 backend in Docker Desktop settings
- This allows Docker to work on Windows Home

**"Hardware assisted virtualization is not enabled"**
- Enable virtualization in your BIOS/UEFI settings
- Look for options like "Intel VT-x" or "AMD-V"

**Volume mounting not working:**
- Ensure Docker Desktop has access to the C: drive
- Settings > Resources > File Sharing > Add C:\

**Slow performance:**
- Don't run Docker containers from network drives
- Keep files on your local C: drive
- Use WSL2 backend instead of Hyper-V

**Line ending issues (scripts fail to run):**
```bash
# If you see "bad interpreter" errors, convert line endings:
dos2unix *.sh
# Or in Docker:
sed -i 's/\r$//' *.sh
```

### General Issues

**API key not working:**
- Verify key is 32 characters
- Check for extra spaces in config file
- Ensure key is quoted: `HIBP_API_KEY="your-key-here"`

**No emails found:**
- Check `my_emails.txt` exists
- Verify `EMAIL_FILE="./my_emails.txt"` in config
- Ensure one email per line, no extra spaces

**Rate limiting errors (429):**
- The script will automatically retry
- Check your API subscription tier
- Adjust `API_DELAY` in config if needed

**Reports not generated:**
- Check `SAVE_REPORTS=true` in config
- Verify `reports/` directory exists
- Check for errors in logs

---

## Performance Comparison

| Method | Startup Time | Ease of Use | Resource Usage | Best For |
|--------|-------------|-------------|----------------|----------|
| **WSL2** | Fast (~2s) | High | Low | Daily use, development |
| **Docker** | Medium (~10s) | Medium | Medium | Isolation, CI/CD |

**Recommendation**: Use WSL2 for regular use and development. Use Docker if you need isolation or are running this in a CI/CD pipeline.

---

## Advanced: Running from Windows PowerShell

### WSL2 Wrapper Script

Create `hibp-check.ps1`:

```powershell
# hibp-check.ps1
# Wrapper to run HIBP checker from Windows PowerShell via WSL2

param(
    [string]$Command = "check"
)

$hibpPath = "~/hibp-checker"

Write-Host "Running HIBP Checker via WSL2..." -ForegroundColor Cyan

wsl bash -c "cd $hibpPath && ./hibp_workflow.sh $Command"

if ($LASTEXITCODE -eq 2) {
    Write-Host "`nCRITICAL: Password exposures detected!" -ForegroundColor Red
    Write-Host "Review the report and change affected passwords immediately." -ForegroundColor Red
} elseif ($LASTEXITCODE -eq 1) {
    Write-Host "`nWarning: Breaches detected. Review the report." -ForegroundColor Yellow
} else {
    Write-Host "`nNo breaches detected." -ForegroundColor Green
}
```

Usage:
```powershell
.\hibp-check.ps1
.\hibp-check.ps1 -Command list-emails
```

### Docker Wrapper Script

Create `hibp-check-docker.ps1`:

```powershell
# hibp-check-docker.ps1
# Wrapper to run HIBP checker via Docker from Windows PowerShell

param(
    [string]$Command = "check"
)

Write-Host "Running HIBP Checker via Docker..." -ForegroundColor Cyan

docker run --rm `
    -v ${PWD}/hibp_config.conf:/app/hibp_config.conf `
    -v ${PWD}/my_emails.txt:/app/my_emails.txt `
    -v ${PWD}/reports:/app/reports `
    -v ${PWD}/logs:/app/logs `
    hibp-checker `
    ./hibp_workflow.sh $Command

if ($LASTEXITCODE -eq 2) {
    Write-Host "`nCRITICAL: Password exposures detected!" -ForegroundColor Red
} elseif ($LASTEXITCODE -eq 1) {
    Write-Host "`nWarning: Breaches detected." -ForegroundColor Yellow
} else {
    Write-Host "`nNo breaches detected." -ForegroundColor Green
}
```

---

## Scheduling Automated Checks on Windows

### Using Windows Task Scheduler with WSL2

1. Open Task Scheduler (`taskschd.msc`)
2. Create Basic Task
3. Name: "HIBP Daily Check"
4. Trigger: Daily at 3:00 AM
5. Action: Start a program
6. Program: `wsl`
7. Arguments: `bash -c "cd ~/hibp-checker && ./hibp_workflow.sh check >> ~/hibp-logs/$(date +\%Y\%m\%d).log 2>&1"`

### Using Task Scheduler with Docker

1. Create `run-hibp-docker.bat`:
```batch
@echo off
cd C:\hibp-checker
docker-compose run --rm hibp-checker ./hibp_workflow.sh check > logs\check-%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1
```

2. Create scheduled task pointing to this batch file

---

## Getting Help

- **HIBP API Issues**: https://haveibeenpwned.com/API/v3
- **WSL2 Issues**: https://docs.microsoft.com/windows/wsl/
- **Docker Issues**: https://docs.docker.com/desktop/windows/
- **Tool Issues**: https://github.com/greogory/hibp-checker/issues

---

*This guide was created to help Windows users run the HIBP Checker, which is natively designed for Linux environments.*
