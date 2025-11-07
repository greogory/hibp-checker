# HIBP Automation Workflow - Project Structure

---

## ⚡ Powered by Have I Been Pwned

This tool uses data from **[Have I Been Pwned](https://haveibeenpwned.com)** by Troy Hunt, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

**Prerequisites**: Requires a **[Have I Been Pwned API subscription](https://haveibeenpwned.com/API/Key)**. See [HIBP API documentation](https://haveibeenpwned.com/API/v3).

---

## Files Overview

```
hibp-automation/
├── hibp_comprehensive_checker.py    # Core Python script - HIBP API client
├── hibp_workflow.sh                  # Main wrapper script with config management
├── claude_code_security_pipeline.sh  # Advanced automation pipeline
├── quick_start.sh                    # Interactive setup and testing
├── hibp_config.conf                  # Configuration file (created on setup)
├── README.md                         # Comprehensive documentation
└── PROJECT_STRUCTURE.md             # This file
```

## Quick Reference

### 1. First Time Setup
```bash
# Option A: Quick interactive setup
./quick_start.sh

# Option B: Manual setup
./hibp_workflow.sh setup
```

### 2. Daily Use with Claude Code
```bash
# Single comprehensive check
claude-code run ./hibp_workflow.sh check

# Full security pipeline
claude-code run ./claude_code_security_pipeline.sh
```

### 3. Direct Python Usage
```bash
# Check multiple emails with verbose output
python3 hibp_comprehensive_checker.py \
    -k YOUR_API_KEY \
    -e email1@example.com email2@example.com \
    -v

# Check from file with JSON output
python3 hibp_comprehensive_checker.py \
    -k YOUR_API_KEY \
    --email-file emails.txt \
    -o json
```

## Key Features by Script

### hibp_comprehensive_checker.py
- Direct HIBP API v3 integration
- Queries breaches, stealer logs, pastes, and pwned passwords
- Multiple output formats (text, JSON, CSV)
- Exit codes for automation (0=clean, 1=breaches, 2=critical)

### hibp_workflow.sh
- Configuration management
- Scheduled checking via cron
- Notification support (Slack, email)
- Report management and cleanup
- Claude Code integration ready

### claude_code_security_pipeline.sh
- Complete security automation workflow
- Risk scoring system
- Automated response actions
- MFA enforcement triggers
- API key rotation
- Emergency lockdown procedures

### quick_start.sh
- Zero-config testing with HIBP test accounts
- Interactive configuration wizard
- Dependency checking and installation
- Immediate validation of setup

## Data Flow

```
1. Input Sources
   ├── Direct emails (-e flag)
   ├── Email file (--email-file)
   └── Configuration (hibp_config.conf)
        ↓
2. HIBP API Queries
   ├── /breachedaccount/{email} - All breaches
   ├── /stealerlogsbyemail/{email} - Credential stuffing
   ├── /pasteaccount/{email} - Public pastes
   └── /range/{hash} - Pwned passwords
        ↓
3. Analysis & Categorization
   ├── Password exposure detection
   ├── Critical site identification
   ├── Stealer log correlation
   └── Risk scoring
        ↓
4. Response Actions
   ├── Report generation
   ├── Notifications
   ├── Automated remediation
   └── Exit codes for CI/CD
```

## API Endpoints Used

| Endpoint | Purpose | Data Retrieved |
|----------|---------|----------------|
| `/breachedaccount/{email}` | Main breach check | All breaches with metadata |
| `/stealerlogsbyemail/{email}` | Credential stuffing | Domains with stolen creds |
| `/pasteaccount/{email}` | Public exposure | Paste sites with email |
| `/range/{hash_prefix}` | Password check | k-anonymity password validation |

## Security Considerations

1. **API Key**: Store in environment variable or secure vault
2. **Passwords**: Hashed before transmission (SHA-1 for API)
3. **Rate Limiting**: Built-in delays and retry logic
4. **Logging**: Sensitive data excluded from logs
5. **Reports**: Store in secure location with proper permissions

## Integration Points

### With CI/CD
```yaml
# GitLab CI example
hibp_check:
  script:
    - ./hibp_workflow.sh check
  only:
    - schedules
  allow_failure: false
```

### With Monitoring
```bash
# Prometheus metrics exporter
./hibp_workflow.sh check | \
  awk '/Total Breaches:/ {print "hibp_breaches_total", $3}' | \
  curl --data-binary @- http://pushgateway:9091/metrics/job/hibp
```

### With SIEM
```bash
# Send to syslog
./hibp_workflow.sh check 2>&1 | \
  logger -t hibp_security -p security.warning
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check API key in config |
| 429 Too Many Requests | Wait for retry-after header |
| No results | Email might not be breached (good!) |
| Script permissions | Run: `chmod +x *.sh *.py` |
| Missing dependencies | Run: `pip3 install requests` |

## Support Levels

- **Basic**: hibp_workflow.sh check
- **Advanced**: claude_code_security_pipeline.sh
- **Custom**: Modify trigger_actions() in scripts

## Exit Codes

- `0`: Clean - no breaches found
- `1`: Warning - breaches detected
- `2`: Critical - passwords compromised or critical sites affected

---

*Designed for Bosco's workflow - combining UNIX expertise with modern security automation*
