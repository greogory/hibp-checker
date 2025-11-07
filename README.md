# HIBP Comprehensive Breach & Credential Stuffing Checker

---

## ⚡ Powered by Have I Been Pwned

**This tool is built on top of the [Have I Been Pwned](https://haveibeenpwned.com) service created by Troy Hunt.**

HIBP is a free service that aggregates data breaches and helps people discover if they've been affected. This project uses HIBP's APIs to provide automated monitoring and comprehensive breach analysis.

### 📜 Attribution & Licensing

This project uses data from **Have I Been Pwned**, licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

- **Breach & Paste Data**: Licensed under CC BY 4.0 - requires clear attribution with link to haveibeenpwned.com
- **Pwned Passwords API**: Freely accessible, no licensing requirements (attribution welcomed)
- **Data Source**: All breach data sourced from [Have I Been Pwned](https://haveibeenpwned.com)

### 🙏 Gratitude

**Immense thanks to Troy Hunt** for creating and maintaining Have I Been Pwned as a free public service. HIBP has helped millions of people secure their online accounts and understand their exposure to data breaches.

**Support HIBP**: Consider [subscribing to HIBP](https://haveibeenpwned.com/API/Key) or [donating](https://haveibeenpwned.com/Donate) to help keep this critical security service running.

### ⚠️ Prerequisites - HIBP API Key Required

**MANDATORY REQUIREMENT**: This tool requires a **Have I Been Pwned API subscription** (Pwned 1-4 tier) to function.

- **Get API Key**: [Subscribe to HIBP API](https://haveibeenpwned.com/API/Key)
- **Subscription Tiers**: Pwned 1, Pwned 2, Pwned 3, or Pwned 4
- **API Terms**: Review [HIBP API documentation](https://haveibeenpwned.com/API/v3) for usage terms
- **License Requirements**: Must provide attribution per CC BY 4.0 license

**The Pwned Passwords API is free and does not require a subscription**, but breach checking, paste monitoring, and stealer log queries require a paid API key.

---

**Platform**: Linux only (bash scripts) | [Windows guide](WINDOWS_INSTALL.md)
**Dependencies**: Python 3.6+, bash, requests library, **HIBP API subscription**
**Claude Code**: Optional (works standalone)

## Overview

This automated workflow goes beyond basic breach checking to provide deep insights into password compromises, stealer logs, and credential stuffing threats from Have I Been Pwned's databases.

This tool is **completely standalone** and does not require Claude Code to run. While it was developed with Claude Code integration in mind, all functionality works independently via command line.

## Key Features

- **Comprehensive Breach Analysis**: Identifies all breaches with detailed categorization
- **Password Exposure Detection**: Tracks which breaches exposed passwords and their storage format (plaintext, MD5, bcrypt, etc.)
- **Stealer Log Mining**: Queries HIBP's stealer log data (including credential stuffing compilations like Synthient)
- **Critical Site Identification**: Flags compromises on banking, cloud, and authentication services
- **Pwned Password Checking**: Validates passwords against 900+ million compromised credentials
- **Multi-format Reporting**: JSON, CSV, and human-readable text reports
- **Standalone Operation**: Works entirely from command line, no external tools required
- **Multiple Email Support**: Monitor unlimited email addresses with a single configuration
- **Optional Claude Code Integration**: Can be used with Claude Code CLI for enhanced automation

## Multiple Email Address Setup

### Option 1: Quick Setup (Recommended)
```bash
# Interactive setup with email configuration
./quick_start.sh

# Choose option 2 when prompted for "many email addresses"
# The script will create my_emails.txt for you
```

### Option 2: Manual Configuration

#### Method A: Direct Email List (Good for 1-5 emails)
Edit `hibp_config.conf`:
```bash
EMAIL_ADDRESSES="bosco@personal.com admin@work.com noreply@service.com"
```

#### Method B: Email File (Recommended for 5+ emails)
Create `my_emails.txt`:
```
# One email per line
bosco@personal.com
admin@work.com
support@myservice.com
legacy@oldprovider.com
noreply@automation.com
```

Then in `hibp_config.conf`:
```bash
EMAIL_FILE="./my_emails.txt"
```

#### Method C: Combine Both
```bash
# Some emails directly
EMAIL_ADDRESSES="critical@admin.com"
# Rest in file
EMAIL_FILE="./bulk_emails.txt"
```

### Email Management Commands
```bash
# Create new email file
./hibp_workflow.sh emails create

# Add email to existing file
./hibp_workflow.sh add-email bosco@newdomain.com

# List all configured emails
./hibp_workflow.sh list-emails

# Validate email formats
./hibp_workflow.sh validate-emails
```

## Automated Monitoring Setup

### 1. Initial Configuration
```bash
# Run interactive setup
./hibp_workflow.sh setup

# Or use quick start
./quick_start.sh
```

### 2. Configure Scheduling
```bash
# Enable automated checks
ENABLE_SCHEDULED_CHECKS=true

# Schedule options:
SCHEDULE="0 3 * * *"     # Daily at 3 AM
SCHEDULE="0 9 * * 1"     # Weekly Monday 9 AM
SCHEDULE="0 */6 * * *"   # Every 6 hours
SCHEDULE="0 0 1 * *"     # Monthly on the 1st
```

### 3. Set Up Notifications
```bash
# In hibp_config.conf:
SEND_NOTIFICATIONS=true
NOTIFICATION_EMAIL="bosco@maindomain.com"
NOTIFY_ONLY_NEW=true  # Only alert on NEW breaches
```

### 4. Apply Schedule
```bash
./hibp_workflow.sh schedule
```

## Rate Limits by Subscription

| Subscription | RPM | Emails/Min | Daily Checks |
|-------------|-----|------------|--------------|
| Pwned 1 | 10 | ~3 | 4,320 |
| Pwned 2 | 50 | ~15 | 21,600 |
| Pwned 3 | 100 | ~30 | 43,200 |
| Pwned 4 | 500 | ~150 | 216,000 |

With Pwned 1, you can comfortably monitor 10-20 emails with multiple daily checks.

## About Synthient & Credential Stuffing Data

The "Synthient Credential Stuffing Threat Data" is incorporated into HIBP's stealer log breaches. These are flagged with `IsStealerLog: true` and represent:

- Credentials captured by info-stealers (malware that grabs saved passwords)
- Compiled lists used for credential stuffing attacks
- Active credentials paired with specific websites (e.g., netflix.com:user@email.com:password)

Our tool specifically queries the stealer log API endpoints to identify where your credentials may be actively exploited.

## System Requirements

- **Operating System**: Linux (tested on CachyOS/Arch, should work on Debian/Ubuntu/Fedora)
- **Python**: 3.6 or higher
- **Shell**: Bash 4.0+
- **Dependencies**: `python3`, `requests` library

> **Note**: This tool is designed specifically for Linux. It will not work on Windows or macOS without modifications due to bash-specific features and script structure.

## Installation

```bash
# Clone the repository
git clone https://github.com/greogory/hibp-checker.git
cd hibp-checker

# Make scripts executable
chmod +x hibp_workflow.sh
chmod +x hibp_comprehensive_checker.py
chmod +x quick_start.sh
chmod +x multi_email_setup.sh

# Install Python dependencies (minimal - uses stdlib mostly)
pip3 install requests
```

## Configuration

### Step 1: Set Your API Key (Recommended: Environment Variable)

**Method 1 (Recommended): Environment Variable**

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
export HIBP_API_KEY="your-32-character-api-key-here"
```

Then reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

**Method 2 (Alternative): Config File**

If you prefer not to use environment variables, you can set the API key in the config file:

```bash
cp hibp_config.conf.example hibp_config.conf
nano hibp_config.conf  # Edit and add your API key
```

> **Security Note**: Environment variables are more secure than storing keys in config files, especially if the config file is version controlled or accessible by other users.

### Step 2: Configure Email Addresses

```bash
# Copy template
cp my_emails_template.txt my_emails.txt

# Edit and add your email addresses (one per line)
nano my_emails.txt
```

### Step 3: Run Your First Check

```bash
./hibp_workflow.sh check
```

## Quick Start for Multiple Emails

```bash
# Option 1: Interactive setup with guided configuration
./quick_start.sh
# Choose option 2 for email file creation
# Add your emails when prompted
# Enable scheduling when asked

# Option 2: Manual setup with email file
cat > my_emails.txt << EOF
bosco@personal.com
admin@work.com
support@service.com
EOF

./hibp_workflow.sh setup
# Point to my_emails.txt when asked for email file

# Option 3: Quick command-line setup
echo "HIBP_API_KEY='your-key-here'" > hibp_config.conf
echo "EMAIL_FILE='./my_emails.txt'" >> hibp_config.conf
./hibp_workflow.sh check
```

## Automation Workflows

### Daily Security Monitoring
```bash
#!/bin/bash
# save as: daily_security_check.sh

# Run HIBP check
./hibp_workflow.sh check
EXIT_CODE=$?

# Handle results based on severity
if [[ $EXIT_CODE -eq 2 ]]; then
    # Critical: passwords compromised
    echo "🚨 CRITICAL SECURITY ALERT"
    # Trigger password reset workflow
    ./initiate_password_resets.sh
    # Lock compromised accounts
    ./lockdown_accounts.sh
elif [[ $EXIT_CODE -eq 1 ]]; then
    # Warning: breaches detected
    echo "⚠️ Security breaches detected"
    # Generate report for security team
    ./generate_security_report.sh
fi
```

### New Breach Detection
The workflow tracks previous results to detect NEW breaches:
```bash
# Automatic tracking in .last_breach_check
# Only notifies when NEW breaches appear
NOTIFY_ONLY_NEW=true
```

### Integration with CI/CD
```yaml
# .gitlab-ci.yml
hibp_security_check:
  stage: security
  script:
    - ./hibp_workflow.sh check
  artifacts:
    paths:
      - reports/
  only:
    - schedules
  allow_failure: false
```

## Configuration Reference

The tool uses `hibp_config.conf` for settings:

```bash
# API Key (RECOMMENDED: Use environment variable instead)
# export HIBP_API_KEY="your-key" in ~/.bashrc or ~/.zshrc
# Leave blank here to use environment variable
HIBP_API_KEY=""

# Email sources (use one or both)
EMAIL_ADDRESSES="user@example.com admin@company.com"
EMAIL_FILE="/path/to/emails.txt"

# Optional password checking
PASSWORDS="TestPass123 OldPassword456"  # Will be hashed before sending
PASSWORD_FILE="/path/to/passwords.txt"

# Output and notifications
OUTPUT_FORMAT="text"  # json, csv, or text
VERBOSE=true
SEND_NOTIFICATIONS=true
SLACK_WEBHOOK="https://hooks.slack.com/services/..."
```

**Priority order for API key:**
1. Environment variable `$HIBP_API_KEY` (recommended)
2. Value set in `hibp_config.conf`

## Usage

### Command Line (Direct)

```bash
# Basic check with config file
./hibp_workflow.sh check

# Direct Python script usage
python3 hibp_comprehensive_checker.py \
    -k YOUR_API_KEY \
    -e email1@example.com email2@example.com \
    -p password1 password2 \
    -o text \
    -v

# Check emails from file
python3 hibp_comprehensive_checker.py \
    -k YOUR_API_KEY \
    --email-file emails.txt \
    --password-file passwords.txt \
    -o json
```

### Claude Code Integration (Optional)

If you're using [Claude Code](https://claude.com/code), you can optionally integrate this tool:

```bash
# One-time setup
claude-code run ./hibp_workflow.sh setup

# Run comprehensive check
claude-code run ./hibp_workflow.sh check

# Schedule automated checks (via cron)
claude-code run ./hibp_workflow.sh schedule
```

**Note**: Claude Code is completely optional. All commands work standalone without it by simply running `./hibp_workflow.sh` directly.

### Automation Workflow

```bash
# Add to your CI/CD pipeline
#!/bin/bash
source hibp_config.conf
./hibp_workflow.sh check
EXIT_CODE=$?

case $EXIT_CODE in
    0) echo "✓ No breaches" ;;
    1) echo "⚠ Breaches found" ;;
    2) echo "🚨 CRITICAL: Passwords compromised!" 
       # Trigger password reset workflow
       ./trigger_password_reset.sh
       ;;
esac
```

## API Endpoints Used

The tool queries these HIBP API v3 endpoints:

1. **Breached Account** (`/breachedaccount/{email}`)
   - Returns all breaches for an email
   - Includes breach metadata and data classes

2. **Stealer Logs by Email** (`/stealerlogsbyemail/{email}`)
   - Returns domains where credentials were captured
   - This includes Synthient and other credential stuffing data

3. **Pastes** (`/pasteaccount/{email}`)
   - Checks if email appears in public pastes

4. **Pwned Passwords** (`/range/{hash_prefix}`)
   - k-anonymity search for compromised passwords
   - No API key required

## Understanding the Results

### Breach Categories

- **Verified**: Legitimately hacked and verified by HIBP
- **Unverified**: Likely legitimate but not independently verified
- **Sensitive**: Adult sites (not returned by public API)
- **Stealer Logs**: Active credentials from malware/credential stuffing

### Password Exposure Types

The tool analyzes breach descriptions to determine password storage:

- `plaintext`: Passwords stored without encryption (CRITICAL)
- `md5_hash`: Weak hashing, easily cracked
- `sha1_hash`: Weak hashing, vulnerable to rainbow tables
- `bcrypt_hash`: Strong hashing, but still change password
- `encrypted`: Unknown encryption method
- `unknown`: Cannot determine from description

### Critical Sites

Automatically flags compromises on:
- Financial: banks, PayPal, Stripe, Square
- Cloud: AWS, Azure, DigitalOcean
- Auth: Google, Microsoft, GitHub
- Social: Facebook, LinkedIn, Twitter

## Exit Codes

- `0`: No breaches detected
- `1`: Breaches found (non-critical)
- `2`: Critical - passwords exposed or critical sites compromised

## Report Formats

### Text Report (Default)
```
HIBP COMPREHENSIVE BREACH REPORT
Generated: 2024-11-07T10:30:00
============================================================

EMAIL: bosco@example.com
------------------------------
Total Breaches: 5
Password Exposed In:
  - Adobe (2013-10-04) - Type: md5_hash
  - LinkedIn (2012-05-05) - Type: sha1_hash

Credentials Stolen For 3 Sites:
  - netflix.com
  - spotify.com
  - github.com

CRITICAL SITES COMPROMISED:
  ⚠️  github.com
```

### JSON Report
Structured data for programmatic processing:
```json
{
  "scan_date": "2024-11-07T10:30:00",
  "emails_checked": [...],
  "summary": {
    "total_breaches": 5,
    "password_exposures": 2,
    "stealer_log_hits": 3,
    "critical_sites_compromised": 1
  }
}
```

## Security Notes

1. **API Key Security**: Store in environment variable or secure vault
2. **Password Handling**: Passwords are SHA-1 hashed before API transmission
3. **k-Anonymity**: Only first 5 characters of password hash sent to API
4. **Rate Limiting**: Built-in delays to respect API limits (varies by subscription)

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Invalid API key
2. **429 Too Many Requests**: Hitting rate limit, script auto-retries
3. **404 Not Found**: Email not in any breaches (good news!)

### Debug Mode

```bash
# Enable verbose logging
VERBOSE=true ./hibp_workflow.sh check

# Test configuration
./hibp_workflow.sh test
```

## Advanced Features

### Custom Actions

Edit `hibp_workflow.sh` to add custom triggers:

```bash
trigger_actions() {
    local severity="$1"
    if [[ "$severity" == "critical" ]]; then
        # Your custom actions
        disable_account "$email"
        force_mfa_enrollment "$email"
        notify_security_team "$report"
    fi
}
```

### Integration Examples

**With Ansible:**
```yaml
- name: Check HIBP breaches
  command: /opt/hibp/hibp_workflow.sh check
  register: hibp_result
  failed_when: hibp_result.rc == 2
```

**With Docker (Linux-based image):**
```dockerfile
FROM python:3.9-slim
COPY hibp_*.py /app/
COPY *.sh /app/
RUN pip install requests && chmod +x /app/*.sh
ENTRYPOINT ["python3", "/app/hibp_comprehensive_checker.py"]
```

## Platform Compatibility

### Linux ✅
Fully supported and tested on:
- CachyOS (Arch-based)
- Ubuntu/Debian
- Fedora/RHEL
- Other Linux distributions with bash 4.0+

### macOS ❌
Not currently supported due to:
- Bash-specific features (requires bash 4.0+, macOS ships with bash 3.2)
- Linux-specific command options
- Path and process handling differences

**Workaround**: Use Docker with a Linux-based image or run in a Linux VM

### Windows ❌
Not supported natively. The bash scripts require a Linux environment.

**Workaround**: Use WSL2 (Windows Subsystem for Linux) or Docker

📖 **[See detailed Windows installation guide](WINDOWS_INSTALL.md)**

## License

MIT - Free for personal and commercial use

## Support

For HIBP API issues: https://haveibeenpwned.com/API/v3
For tool issues: Create an issue or PR

---

*Built for Bosco's automation workflow - because knowing is half the battle, and automation is the other half.*
