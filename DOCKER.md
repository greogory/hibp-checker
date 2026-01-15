# HIBP Checker - Docker Usage Guide

---

## ⚡ Powered by Have I Been Pwned

This tool uses data from **[Have I Been Pwned](https://haveibeenpwned.com)** by Troy Hunt, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

**Prerequisites**: Requires a **[Have I Been Pwned API subscription](https://haveibeenpwned.com/API/Key)** (Pwned 1-4 tier).

---

## Overview

The HIBP Checker Docker image provides **cross-platform support** for Windows and macOS users, eliminating the need for bash installation and Python environment setup.

> **Note**: Windows and macOS support via Docker is provided but **untested by the maintainer** (no native dev environment available). The image is built on Linux and should work on all platforms with Docker installed. Community feedback and issue reports are welcome!

### Why Use Docker?

- ✅ **Cross-platform**: Works on Windows, macOS, and Linux
- ✅ **No installation**: No need to install Python, bash, or dependencies
- ✅ **Consistent environment**: Same experience across all platforms
- ✅ **Isolated**: Doesn't interfere with your system
- ✅ **Easy updates**: Pull latest image to update

---

## Quick Start

### Prerequisites

1. **Docker installed**:
   - **Windows/Mac**: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - **Linux**: `sudo apt-get install docker.io` or equivalent

2. **HIBP API Key**: [Get yours here](https://haveibeenpwned.com/API/Key)

### One-Line Check

Check a single email address:

```bash
docker run --rm \
  -e HIBP_API_KEY="your-api-key-here" \
  ghcr.io/greogory/hibp-checker:latest \
  python3 hibp_comprehensive_checker.py -e email@example.com -o text -v
```

---

## Installation Methods

### Method 1: Docker Run (Quick Checks)

**Check single email**:
```bash
docker run --rm \
  -e HIBP_API_KEY="your-api-key" \
  -v $(pwd)/reports:/app/reports \
  ghcr.io/greogory/hibp-checker:latest \
  python3 hibp_comprehensive_checker.py -e email@example.com -o text -v
```

**Check multiple emails from file**:
```bash
# Create email list
cat > my_emails.txt <<EOF
email1@example.com
email2@example.com
email3@example.com
EOF

# Run check
docker run --rm \
  -e HIBP_API_KEY="your-api-key" \
  -v $(pwd)/my_emails.txt:/app/data/emails.txt:ro \
  -v $(pwd)/reports:/app/reports \
  ghcr.io/greogory/hibp-checker:latest \
  python3 hibp_comprehensive_checker.py --email-file /app/data/emails.txt -o text -v
```

### Method 2: Docker Compose (Recommended)

**Step 1: Create docker-compose.yml**

```bash
# Download docker-compose.yml
curl -O https://raw.githubusercontent.com/greogory/hibp-checker/main/docker-compose.yml
```

Or create manually:

```yaml
services:
  hibp-checker:
    image: ghcr.io/greogory/hibp-checker:latest
    environment:
      - HIBP_API_KEY=${HIBP_API_KEY}
    volumes:
      - ./my_emails.txt:/app/data/my_emails.txt:ro
      - ./reports:/app/reports
      - ./logs:/app/logs
    command: python3 hibp_comprehensive_checker.py --email-file /app/data/my_emails.txt -o text -v
```

**Step 2: Create .env file**

```bash
echo "HIBP_API_KEY=your-api-key-here" > .env
```

**Step 3: Create email list**

```bash
cat > my_emails.txt <<EOF
email1@example.com
email2@example.com
EOF
```

**Step 4: Run**

```bash
docker-compose up
```

### Method 3: Build Locally

If you want to build from source:

```bash
# Clone repository
git clone https://github.com/greogory/hibp-checker.git
cd hibp-checker

# Build image
docker build -t hibp-checker:local .

# Run
docker run --rm \
  -e HIBP_API_KEY="your-api-key" \
  hibp-checker:local \
  python3 hibp_comprehensive_checker.py -e email@example.com -o text
```

---

## Platform-Specific Instructions

### Windows (PowerShell)

```powershell
# Set API key
$env:HIBP_API_KEY = "your-api-key-here"

# Create email list
@"
email1@example.com
email2@example.com
"@ | Out-File -FilePath my_emails.txt -Encoding UTF8

# Run check
docker run --rm `
  -e HIBP_API_KEY="$env:HIBP_API_KEY" `
  -v ${PWD}/my_emails.txt:/app/data/emails.txt:ro `
  -v ${PWD}/reports:/app/reports `
  ghcr.io/greogory/hibp-checker:latest `
  python3 hibp_comprehensive_checker.py --email-file /app/data/emails.txt -o text -v
```

### Windows (Command Prompt)

```cmd
REM Set API key
set HIBP_API_KEY=your-api-key-here

REM Create email list
echo email1@example.com > my_emails.txt
echo email2@example.com >> my_emails.txt

REM Run check
docker run --rm ^
  -e HIBP_API_KEY=%HIBP_API_KEY% ^
  -v %cd%/my_emails.txt:/app/data/emails.txt:ro ^
  -v %cd%/reports:/app/reports ^
  ghcr.io/greogory/hibp-checker:latest ^
  python3 hibp_comprehensive_checker.py --email-file /app/data/emails.txt -o text -v
```

### macOS

```bash
# Set API key
export HIBP_API_KEY="your-api-key-here"

# Create email list
cat > my_emails.txt <<EOF
email1@example.com
email2@example.com
EOF

# Run check
docker run --rm \
  -e HIBP_API_KEY="$HIBP_API_KEY" \
  -v $(pwd)/my_emails.txt:/app/data/emails.txt:ro \
  -v $(pwd)/reports:/app/reports \
  ghcr.io/greogory/hibp-checker:latest \
  python3 hibp_comprehensive_checker.py --email-file /app/data/emails.txt -o text -v
```

### Linux

```bash
# Set API key
export HIBP_API_KEY="your-api-key-here"

# Create email list
cat > my_emails.txt <<EOF
email1@example.com
email2@example.com
EOF

# Run check
docker run --rm \
  -e HIBP_API_KEY="$HIBP_API_KEY" \
  -v $(pwd)/my_emails.txt:/app/data/emails.txt:ro \
  -v $(pwd)/reports:/app/reports \
  ghcr.io/greogory/hibp-checker:latest \
  python3 hibp_comprehensive_checker.py --email-file /app/data/emails.txt -o text -v
```

---

## Common Use Cases

### 1. Quick Email Check

```bash
docker run --rm \
  -e HIBP_API_KEY="your-key" \
  ghcr.io/greogory/hibp-checker:latest \
  python3 hibp_comprehensive_checker.py -e email@example.com -o text
```

### 2. Check Multiple Emails with Report

```bash
docker run --rm \
  -e HIBP_API_KEY="your-key" \
  -v $(pwd)/my_emails.txt:/app/data/emails.txt:ro \
  -v $(pwd)/reports:/app/reports \
  ghcr.io/greogory/hibp-checker:latest \
  python3 hibp_comprehensive_checker.py \
    --email-file /app/data/emails.txt \
    -o json \
    -v
```

### 3. Check Password

```bash
docker run --rm \
  -e HIBP_API_KEY="your-key" \
  ghcr.io/greogory/hibp-checker:latest \
  python3 hibp_comprehensive_checker.py \
    -e email@example.com \
    -p "MyPassword123" \
    -o text
```

### 4. Generate JSON Report

```bash
docker run --rm \
  -e HIBP_API_KEY="your-key" \
  -v $(pwd)/reports:/app/reports \
  ghcr.io/greogory/hibp-checker:latest \
  python3 hibp_comprehensive_checker.py \
    -e email@example.com \
    -o json > report.json
```

### 5. Scheduled Check (Cron/Task Scheduler)

**Linux/macOS (cron)**:
```bash
# Add to crontab -e
0 3 * * * docker run --rm \
  -e HIBP_API_KEY="your-key" \
  -v /path/to/emails.txt:/app/data/emails.txt:ro \
  -v /path/to/reports:/app/reports \
  ghcr.io/greogory/hibp-checker:latest \
  python3 hibp_comprehensive_checker.py --email-file /app/data/emails.txt -o text
```

**Windows (Task Scheduler)**:
Create a batch file `hibp-check.bat`:
```batch
docker run --rm ^
  -e HIBP_API_KEY=your-key ^
  -v C:\path\to\emails.txt:/app/data/emails.txt:ro ^
  -v C:\path\to\reports:/app/reports ^
  ghcr.io/greogory/hibp-checker:latest ^
  python3 hibp_comprehensive_checker.py --email-file /app/data/emails.txt -o text
```

Then schedule in Task Scheduler to run daily.

---

## Volume Mounts Explained

### Input Files (Read-Only)

Mount your email/password lists as read-only:

```bash
-v $(pwd)/my_emails.txt:/app/data/my_emails.txt:ro
```

- `$(pwd)/my_emails.txt` - File on your host machine
- `/app/data/my_emails.txt` - Path inside container
- `:ro` - Read-only (recommended for input files)

### Output Directories

Mount directories for reports and logs:

```bash
-v $(pwd)/reports:/app/reports
-v $(pwd)/logs:/app/logs
```

Reports will be created in `./reports/` on your host machine.

### Custom Config (Optional)

```bash
-v $(pwd)/hibp_config.conf:/app/hibp_config.conf:ro
```

---

## Environment Variables

### Required

- `HIBP_API_KEY` - Your HIBP API subscription key

### Optional

Can be set via `-e` flag:

```bash
docker run --rm \
  -e HIBP_API_KEY="your-key" \
  -e VERBOSE=true \
  -e OUTPUT_FORMAT=json \
  ghcr.io/greogory/hibp-checker:latest \
  python3 hibp_comprehensive_checker.py -e email@example.com
```

---

## Available Tags

The Docker image is published with multiple tags:

- `latest` - Latest stable version from main branch
- `v2.3.2.2` - Specific version (semantic versioning)
- `v2.3` - Major.minor version
- `v2` - Major version only
- `main` - Latest commit on main branch (may be unstable)
- `sha-abc1234` - Specific commit SHA

### Recommended Tags

**Production**: Use specific version tags
```bash
docker pull ghcr.io/greogory/hibp-checker:v2.3.2.2
```

**Testing**: Use latest
```bash
docker pull ghcr.io/greogory/hibp-checker:latest
```

---

## Docker Compose Examples

### Basic Check

```yaml
services:
  hibp-check:
    image: ghcr.io/greogory/hibp-checker:latest
    environment:
      - HIBP_API_KEY=${HIBP_API_KEY}
    volumes:
      - ./my_emails.txt:/app/data/emails.txt:ro
      - ./reports:/app/reports
    command: python3 hibp_comprehensive_checker.py --email-file /app/data/emails.txt -o text -v
```

Run: `docker-compose up`

### Scheduled Monitoring

```yaml
services:
  hibp-monitor:
    image: ghcr.io/greogory/hibp-checker:latest
    environment:
      - HIBP_API_KEY=${HIBP_API_KEY}
    volumes:
      - ./my_emails.txt:/app/data/emails.txt:ro
      - ./reports:/app/reports
      - ./logs:/app/logs
    command: sh -c "while true; do python3 hibp_comprehensive_checker.py --email-file /app/data/emails.txt -o json; sleep 86400; done"
    restart: unless-stopped
```

This runs a check every 24 hours.

---

## Troubleshooting

### Issue: "Permission denied" on Windows

**Problem**: Docker can't access mounted files

**Solution**:
1. Open Docker Desktop → Settings → Resources → File Sharing
2. Add the directory containing your files
3. Click "Apply & Restart"

### Issue: Reports not appearing

**Problem**: Volume mount not working

**Solution**: Use absolute paths:
```bash
# Windows PowerShell
docker run -v ${PWD}/reports:/app/reports ...

# Windows CMD
docker run -v %cd%/reports:/app/reports ...

# Linux/macOS
docker run -v $(pwd)/reports:/app/reports ...
```

### Issue: "invalid reference format"

**Problem**: Spaces in paths on Windows

**Solution**: Quote the paths:
```bash
docker run -v "C:\Users\My Name\reports:/app/reports" ...
```

### Issue: Container exits immediately

**Problem**: No command specified or invalid command

**Solution**: Check the command is correct:
```bash
docker run --rm \
  -e HIBP_API_KEY="your-key" \
  ghcr.io/greogory/hibp-checker:latest \
  python3 hibp_comprehensive_checker.py --help
```

### Issue: "401 Unauthorized"

**Problem**: Invalid or missing API key

**Solution**: Verify your API key:
```bash
# Check environment variable is set
docker run --rm \
  -e HIBP_API_KEY="your-key" \
  ghcr.io/greogory/hibp-checker:latest \
  sh -c 'echo $HIBP_API_KEY'
```

---

## Building for Multiple Architectures

The image supports both `linux/amd64` and `linux/arm64` (Apple Silicon).

### Build Locally for Your Platform

```bash
docker build -t hibp-checker:local .
```

### Build for Multiple Platforms

Requires Docker Buildx:

```bash
docker buildx create --use
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/greogory/hibp-checker:latest \
  --push \
  .
```

---

## Security Considerations

### API Key Protection

**Do NOT** hardcode your API key in Dockerfiles or docker-compose.yml files that might be committed to Git.

**Good** (using .env file):
```yaml
environment:
  - HIBP_API_KEY=${HIBP_API_KEY}
```

```bash
# .env file (add to .gitignore!)
HIBP_API_KEY=your-actual-key
```

**Bad** (hardcoded):
```yaml
environment:
  - HIBP_API_KEY=abc123def456  # DON'T DO THIS!
```

### Running as Non-Root

The Docker image runs as user `hibpuser` (UID 1000), not root, for security.

### File Permissions

Output files are created with permissions of the container user (UID 1000).

On Linux, if you need different ownership:
```bash
docker run --rm \
  --user $(id -u):$(id -g) \
  -e HIBP_API_KEY="your-key" \
  -v $(pwd)/reports:/app/reports \
  ghcr.io/greogory/hibp-checker:latest \
  python3 hibp_comprehensive_checker.py -e email@example.com -o text
```

---

## Performance Tips

### Use Specific Tags

Avoid pulling `:latest` every time:

```bash
# Pull once
docker pull ghcr.io/greogory/hibp-checker:v2.3.2.2

# Use specific tag
docker run ghcr.io/greogory/hibp-checker:v2.3.2.2 ...
```

### Remove Old Containers

Containers with `--rm` are automatically removed, but if you don't use `--rm`:

```bash
# List containers
docker ps -a

# Remove stopped containers
docker container prune
```

### Remove Old Images

```bash
# List images
docker images

# Remove unused images
docker image prune -a
```

---

## Comparison: Docker vs Native

### Docker Advantages

- ✅ Cross-platform (Windows/macOS/Linux)
- ✅ No dependency installation
- ✅ Consistent environment
- ✅ Isolated from host system
- ✅ Easy updates (pull new image)

### Native Advantages

- ✅ Slightly faster (no container overhead)
- ✅ Direct filesystem access
- ✅ No Docker installation required
- ✅ Easier to modify scripts

### Recommendation

- **Windows/macOS users**: Use Docker
- **Linux users**: Either works (native is simpler if you already have Python/bash)
- **CI/CD pipelines**: Use Docker for consistency

---

## Getting Help

### View Image Info

```bash
docker inspect ghcr.io/greogory/hibp-checker:latest
```

### Check Container Logs

```bash
# If running in background
docker logs hibp-checker

# Follow logs in real-time
docker logs -f hibp-checker
```

### Shell Into Container

```bash
docker run -it --rm \
  -e HIBP_API_KEY="your-key" \
  ghcr.io/greogory/hibp-checker:latest \
  bash
```

### Run Tests

```bash
docker run --rm \
  -e HIBP_API_KEY="your-key" \
  ghcr.io/greogory/hibp-checker:latest \
  python3 hibp_comprehensive_checker.py -e test@example.com -o text -v
```

---

## Quick Reference Card

### Pull Image
```bash
docker pull ghcr.io/greogory/hibp-checker:latest
```

### Check Single Email
```bash
docker run --rm -e HIBP_API_KEY="key" ghcr.io/greogory/hibp-checker:latest python3 hibp_comprehensive_checker.py -e email@example.com -o text
```

### Check Multiple Emails
```bash
docker run --rm -e HIBP_API_KEY="key" -v $(pwd)/emails.txt:/app/data/emails.txt:ro ghcr.io/greogory/hibp-checker:latest python3 hibp_comprehensive_checker.py --email-file /app/data/emails.txt -o text
```

### With Reports
```bash
docker run --rm -e HIBP_API_KEY="key" -v $(pwd)/reports:/app/reports ghcr.io/greogory/hibp-checker:latest python3 hibp_comprehensive_checker.py -e email@example.com -o json
```

### Docker Compose
```bash
# Setup
echo "HIBP_API_KEY=your-key" > .env
echo "email@example.com" > my_emails.txt

# Run
docker-compose up
```

---

## Links

- **Docker Hub**: Not published (using GitHub Container Registry instead)
- **GitHub Container Registry**: https://github.com/greogory/hibp-checker/pkgs/container/hibp-checker
- **Source Code**: https://github.com/greogory/hibp-checker
- **Issues**: https://github.com/greogory/hibp-checker/issues
- **HIBP API**: https://haveibeenpwned.com/API/v3

---

**Last Updated:** 2026-01-09
**Image Version:** 2.3.2.2
**Supported Platforms:** linux/amd64, linux/arm64
