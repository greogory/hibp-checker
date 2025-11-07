# GitHub Security Setup Guide

This guide walks you through setting up GitHub's built-in security features to protect your HIBP Checker repository from malicious contributions.

## Table of Contents
1. [Branch Protection Rules](#branch-protection-rules)
2. [Security Settings](#security-settings)
3. [GitHub Actions Workflow](#github-actions-workflow)
4. [Code Scanning](#code-scanning)
5. [Verification Steps](#verification-steps)

---

## Branch Protection Rules

Protect the `main` branch from unauthorized or dangerous changes.

### Setup Steps

1. **Navigate to Branch Protection**
   - Go to: https://github.com/greogory/hibp-checker/settings/branches
   - Click "Add rule" or "Add branch protection rule"

2. **Branch Name Pattern**
   - Enter: `main`

3. **Enable These Rules**

   #### Require Pull Request Reviews
   - ☑️ **Require a pull request before merging**
     - Required approvals: `1`
     - ☑️ Dismiss stale pull request approvals when new commits are pushed
     - ☑️ Require review from Code Owners (if you add CODEOWNERS file)

   #### Status Checks
   - ☑️ **Require status checks to pass before merging**
     - ☑️ Require branches to be up to date before merging
     - Once GitHub Actions workflow is added, select: `security-scan`

   #### Conversation Resolution
   - ☑️ **Require conversation resolution before merging**
     - All review comments must be resolved

   #### Restrictions
   - ☑️ **Restrict who can push to matching branches**
     - Add your username: `greogory`
     - Or leave empty to allow maintainers only

   #### Rules Applied to Admins
   - ☑️ **Do not allow bypassing the above settings**
     - Ensures even repository admins follow the rules

   #### Force Pushes
   - ☑️ **Do not allow force pushes**
     - Prevents rewriting git history

   #### Deletions
   - ☑️ **Do not allow deletions**
     - Prevents accidental branch deletion

4. **Click "Create"** or "Save changes"

### What This Protects Against

- ✅ Direct pushes to main (forces PR workflow)
- ✅ Merging without code review
- ✅ Merging with failing security checks
- ✅ Unresolved security concerns in reviews
- ✅ Force pushes that rewrite history
- ✅ Accidental branch deletion

---

## Security Settings

Enable GitHub's automated security features.

### Setup Steps

1. **Navigate to Security Settings**
   - Go to: https://github.com/greogory/hibp-checker/settings/security_analysis

2. **Enable Dependabot Alerts**
   - ☑️ **Dependabot alerts**
     - Notifies you of vulnerabilities in dependencies
     - Click "Enable" if not already enabled

3. **Enable Dependabot Security Updates**
   - ☑️ **Dependabot security updates**
     - Automatically creates PRs to update vulnerable dependencies
     - Click "Enable"

4. **Enable Private Vulnerability Reporting**
   - Go to: https://github.com/greogory/hibp-checker/settings
   - Scroll to "Security" section
   - ☑️ **Private vulnerability reporting**
     - Allows security researchers to report issues privately
     - Click "Enable"

5. **Secret Scanning** (if available - requires public repo or GitHub Advanced Security)
   - ☑️ **Secret scanning**
     - Detects API keys, tokens, and other secrets in code
     - Click "Enable" if available

### Additional Security Settings

1. **Disable Unused Features** (reduces attack surface)
   - Go to: https://github.com/greogory/hibp-checker/settings
   - Features section:
     - ☐ Wikis (disable if not used)
     - ☐ Issues (or enable with moderation)
     - ☐ Sponsorships (unless needed)
     - ☐ Projects (unless used)

2. **Moderate Comments** (if issues/PRs enabled)
   - Settings > Moderation
   - ☑️ Enable comment moderation
   - Add blocked users if needed

---

## GitHub Actions Workflow

The security-checks.yml workflow needs to be manually added due to token permissions.

### Setup Steps

1. **Authorize Workflow Scope**
   ```bash
   gh auth refresh -h github.com -s workflow
   ```
   Follow the prompts to authorize the workflow scope.

2. **Push Workflow File**
   ```bash
   cd ~/claude-archive/projects/hibp-project/
   git add .github/workflows/security-checks.yml
   git commit -m "Add automated security checks workflow"
   git push
   ```

3. **Verify Workflow**
   - Go to: https://github.com/greogory/hibp-checker/actions
   - You should see "Security Checks" workflow
   - Make a test commit to trigger it

### What the Workflow Checks

- ✅ Hardcoded API keys
- ✅ .gitignore integrity
- ✅ Sensitive data patterns
- ✅ Python dependency vulnerabilities
- ✅ Accidentally committed reports
- ✅ Dangerous logging patterns
- ✅ Script permissions

---

## Code Scanning

Set up advanced code scanning for additional security.

### Option 1: GitHub Advanced Security (Free for Public Repos)

1. **Enable Code Scanning**
   - Go to: https://github.com/greogory/hibp-checker/security/code-scanning
   - Click "Set up code scanning"

2. **Configure CodeQL**
   - Select "Advanced" setup
   - Choose "CodeQL Analysis"
   - Select languages: Python, Shell

3. **Review and Commit**
   - GitHub will create a PR with the workflow
   - Review and merge

### Option 2: Third-Party Tools

**Snyk** (Free for open source):
1. Go to: https://snyk.io/
2. Sign in with GitHub
3. Add repository: `hibp-checker`
4. Enable automatic PRs

**SonarCloud** (Free for open source):
1. Go to: https://sonarcloud.io/
2. Sign in with GitHub
3. Analyze: `greogory/hibp-checker`

---

## Verification Steps

### 1. Test Branch Protection

Try to push directly to main (should fail):
```bash
cd ~/claude-archive/projects/hibp-project/
echo "test" >> README.md
git add README.md
git commit -m "test direct push"
git push
```

Expected result: ❌ Push rejected (branch protection)

### 2. Test Pre-Commit Hook

Try to commit sensitive file (should fail):
```bash
git add hibp_config.conf
git commit -m "test"
```

Expected result: ❌ Commit blocked by pre-commit hook

### 3. Test Pull Request Workflow

1. Create a new branch:
   ```bash
   git checkout -b test-security
   echo "# Test" >> SECURITY.md
   git add SECURITY.md
   git commit -m "test security"
   git push origin test-security
   ```

2. Create PR on GitHub:
   - Go to: https://github.com/greogory/hibp-checker/pulls
   - Click "New pull request"
   - Base: main, Compare: test-security
   - Create PR

3. Verify:
   - ✅ Security checks run automatically
   - ✅ Requires approval before merge
   - ✅ Can't merge until checks pass

### 4. Test Dependabot

Wait for Dependabot to scan dependencies:
- Check: https://github.com/greogory/hibp-checker/security/dependabot

Expected result: ✅ No vulnerabilities (or PRs created if any found)

### 5. Verify Security Policy

Check that security policy is visible:
- Go to: https://github.com/greogory/hibp-checker/security/policy

Expected result: ✅ SECURITY.md displayed

---

## Security Checklist

Use this checklist to verify all protections are in place:

### Repository Settings
- [ ] Branch protection enabled on `main`
- [ ] Require PR reviews (1 approval)
- [ ] Require status checks
- [ ] Require conversation resolution
- [ ] No force pushes allowed
- [ ] No deletions allowed
- [ ] Rules apply to admins

### Security Features
- [ ] Dependabot alerts enabled
- [ ] Dependabot security updates enabled
- [ ] Private vulnerability reporting enabled
- [ ] Secret scanning enabled (if available)
- [ ] Code scanning configured (optional)

### Local Protections
- [ ] Pre-commit hook installed and executable
- [ ] Pre-commit hook tested
- [ ] .gitignore protects sensitive files

### CI/CD
- [ ] GitHub Actions workflow added
- [ ] Workflow runs on PR and push
- [ ] Security checks pass

### Documentation
- [ ] SECURITY.md visible on GitHub
- [ ] Security policy linked in repo
- [ ] Contributing guidelines include security notes

---

## Maintenance

### Weekly
- [ ] Review open PRs for security concerns
- [ ] Check Dependabot alerts

### Monthly
- [ ] Review security workflow logs
- [ ] Update dependencies if needed
- [ ] Review access permissions

### Quarterly
- [ ] Full security audit
- [ ] Review and update SECURITY.md
- [ ] Test all security protections

---

## Common Issues

### Issue: Can't Push to Main

**Problem:** Direct push to main blocked

**Solution:** This is correct behavior. Create a PR instead:
```bash
git checkout -b feature-branch
# Make changes
git push origin feature-branch
# Create PR on GitHub
```

### Issue: Pre-commit Hook Not Running

**Problem:** Hook doesn't execute

**Solution:** Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Issue: Workflow Permission Denied

**Problem:** Can't push GitHub Actions workflow

**Solution:** Grant workflow scope:
```bash
gh auth refresh -h github.com -s workflow
```

Then retry push.

### Issue: Dependabot PRs Failing

**Problem:** Dependabot PRs don't pass security checks

**Solution:** Review the PR, ensure it doesn't introduce vulnerabilities, then approve if safe.

---

## Getting Help

**GitHub Documentation:**
- Branch Protection: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches
- Dependabot: https://docs.github.com/en/code-security/dependabot
- Code Scanning: https://docs.github.com/en/code-security/code-scanning

**Repository Issues:**
- Create issue: https://github.com/greogory/hibp-checker/issues

---

**Last Updated:** 2025-11-07
**Status:** Active Protection Measures
