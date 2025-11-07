# GitHub Pull Request Approval Workflow Guide

---

## ⚡ Powered by Have I Been Pwned

This tool uses data from **[Have I Been Pwned](https://haveibeenpwned.com)** by Troy Hunt, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

## Overview

This guide explains how to set up and use GitHub's Pull Request approval workflow to protect your main branch from unauthorized changes.

## Table of Contents

1. [How GitHub Approvals Work](#how-github-approvals-work)
2. [Setting Up Branch Protection](#setting-up-branch-protection)
3. [How to Approve Pull Requests](#how-to-approve-pull-requests)
4. [Common Scenarios](#common-scenarios)
5. [Troubleshooting](#troubleshooting)

---

## How GitHub Approvals Work

### The Pull Request Workflow

When branch protection with required approvals is enabled:

1. **Changes Must Go Through PRs**: You cannot push directly to `main`
2. **PR Requires Review**: Each PR needs approval(s) before merging
3. **You Approve Your Own PRs**: As repo owner, you can approve your own PRs
4. **After Approval, You Can Merge**: Once approved, the merge button becomes available

### Key Concepts

- **Pull Request (PR)**: A proposed change that needs review
- **Review**: Your examination of the PR changes
- **Approval**: Your explicit "yes, this is good" decision
- **Merge**: Incorporating the approved changes into main branch

---

## Setting Up Branch Protection

### Step 1: Navigate to Branch Protection Settings

Go to: https://github.com/greogory/hibp-checker/settings/branches

Or:
1. Go to your repository
2. Click **Settings** (top right)
3. Click **Branches** (left sidebar)
4. Find "Branch protection rules"

### Step 2: Add/Edit Rule for Main Branch

If no rule exists:
- Click **Add branch protection rule**
- Branch name pattern: `main`

If rule exists:
- Click **Edit** next to the existing `main` rule

### Step 3: Configure Required Approvals

Enable these settings:

#### ☑️ Require a pull request before merging
- **Required approvals**: `1`
- ☑️ **Dismiss stale pull request approvals when new commits are pushed**
  - This ensures new changes get re-reviewed
- ☐ **Require review from Code Owners** (optional - only if you have a CODEOWNERS file)
- ☑️ **Require approval of the most recent reviewable push**
  - Ensures the latest changes are approved

#### ☑️ Require status checks to pass before merging (recommended)
- Select: `security-scan` (if GitHub Actions workflow is running)

#### ☑️ Require conversation resolution before merging
- All review comments must be resolved

#### ☑️ Require signed commits (you already have this)
- Ensures all commits are GPG-signed

#### Important: Do NOT Enable These
- ☐ **Do not allow bypassing the above settings** - Leave UNCHECKED
  - If checked, even you (as admin) cannot approve your own PRs
  - For solo projects, you need to be able to approve your own PRs

### Step 4: Save Changes

Click **Save changes** at the bottom

---

## How to Approve Pull Requests

### Method 1: GitHub Web Interface (Recommended)

#### Step 1: Navigate to Your Pull Request

Go to: https://github.com/greogory/hibp-checker/pulls

Or click the PR link that appears when you push a branch:
```
remote: Create a pull request for 'your-branch' on GitHub by visiting:
remote:      https://github.com/greogory/hibp-checker/pull/new/your-branch
```

#### Step 2: Review the Changes

1. **Click on the PR** to open it
2. **Click "Files changed" tab** to see what was modified
3. **Review each file**:
   - Green lines = added
   - Red lines = removed
   - Look for:
     - Accidental sensitive data
     - Security issues
     - Code quality problems

#### Step 3: Start Your Review

Click the **"Review changes"** button (top right of Files changed tab)

#### Step 4: Submit Your Approval

A dialog box appears with three options:

1. **Comment**: Just leave a comment, no approval
2. **Approve**: ✅ **Select this one** to approve the PR
3. **Request changes**: Ask for modifications before approval

**To approve:**
- Select **"Approve"** radio button
- Optionally add a comment like: "LGTM" (Looks Good To Me) or "Approved"
- Click **"Submit review"**

#### Step 5: Merge the Pull Request

After approval, the **"Merge pull request"** button becomes green and clickable:

1. Click **"Merge pull request"**
2. Choose merge method:
   - **Create a merge commit** (default)
   - **Squash and merge** (recommended for clean history)
   - **Rebase and merge**
3. Confirm by clicking **"Confirm merge"** or **"Confirm squash and merge"**
4. Optionally delete the branch after merge

### Method 2: GitHub CLI (gh)

From your terminal:

```bash
# View pull requests
gh pr list

# View a specific PR
gh pr view 5

# Review and approve a PR
gh pr review 5 --approve --body "Approved - looks good"

# Merge the PR after approval
gh pr merge 5 --squash --delete-branch
```

### Method 3: Review in Your Editor

```bash
# Checkout the PR branch locally
gh pr checkout 5

# Review the changes
git diff main

# If good, go back to GitHub web interface to approve
# (Cannot approve from command line without additional API calls)
```

---

## Common Scenarios

### Scenario 1: Making Changes to Main Branch

**Before (without branch protection):**
```bash
git checkout main
echo "change" >> README.md
git add README.md
git commit -m "update readme"
git push origin main  # ✅ Works
```

**After (with branch protection):**
```bash
git checkout main
echo "change" >> README.md
git add README.md
git commit -m "update readme"
git push origin main  # ❌ REJECTED - branch is protected
```

**Correct workflow:**
```bash
# 1. Create feature branch
git checkout -b update-readme

# 2. Make changes
echo "change" >> README.md
git add README.md
git commit -m "update readme"

# 3. Push to feature branch
git push -u origin update-readme

# 4. Create PR (GitHub will show you a link, or use gh CLI)
gh pr create --title "Update README" --body "Updated readme with new info"

# 5. Go to GitHub web interface and approve the PR
# Visit: https://github.com/greogory/hibp-checker/pulls
# Click your PR → Files changed → Review changes → Approve → Submit review

# 6. Merge the PR
gh pr merge --squash --delete-branch
# Or use the web interface

# 7. Update local main
git checkout main
git pull origin main
```

### Scenario 2: Claude Code Making Changes

When Claude Code makes changes and commits:

```bash
# Claude creates a branch and pushes
# You see: https://github.com/greogory/hibp-checker/pull/new/claude-changes

# You need to:
# 1. Click the link to create PR
# 2. Review the changes in "Files changed" tab
# 3. Click "Review changes" → "Approve" → "Submit review"
# 4. Click "Merge pull request" → "Confirm squash and merge"
```

### Scenario 3: Approving Your Own PR as Solo Developer

**This is completely normal and expected for solo projects!**

1. You create a PR with your changes
2. You review your own code
3. You approve your own PR
4. You merge your own PR

**Why this is okay:**
- You're the only developer
- You're doing a self-code-review (good practice)
- Branch protection still prevents accidental direct pushes
- You still benefit from:
  - Reviewing your changes before merging
  - Running CI/CD checks
  - Maintaining clean git history
  - Preventing accidental force pushes

---

## Visual Guide: Approval Process

### When You Open a PR

```
┌─────────────────────────────────────────┐
│  Pull Request #5                        │
│  ┌───────────────────────────────────┐ │
│  │ Conversation │ Commits │ Files   │ │
│  │              │         │ changed │ │  ← Click "Files changed"
│  └───────────────────────────────────┘ │
│                                         │
│  ⚠️  Review required                    │
│  This PR requires 1 approval            │
│                                         │
│  [Merge pull request ▼] (grayed out)   │
└─────────────────────────────────────────┘
```

### After Clicking "Files changed"

```
┌─────────────────────────────────────────┐
│  Files changed                          │
│                                         │
│  📄 README.md                           │
│  + Added line                           │
│  - Removed line                         │
│                                         │
│         [Review changes ▼] ← Click here│
└─────────────────────────────────────────┘
```

### Review Dialog

```
┌─────────────────────────────────────────┐
│  Review changes                         │
│  ┌───────────────────────────────────┐ │
│  │ Leave a comment (optional)        │ │
│  │                                   │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ○ Comment                              │
│  ◉ Approve          ← Select this      │
│  ○ Request changes                      │
│                                         │
│  [Submit review]    ← Click to approve │
└─────────────────────────────────────────┘
```

### After Approval

```
┌─────────────────────────────────────────┐
│  Pull Request #5                        │
│                                         │
│  ✅ You approved these changes          │
│  ✅ All checks passed                   │
│                                         │
│  [Merge pull request ▼] ← Now clickable│
│                                         │
│  └─ [Confirm squash and merge]         │
└─────────────────────────────────────────┘
```

---

## Step-by-Step Example

Let's walk through a complete example:

### 1. You Make Changes via Claude Code

```bash
# Claude creates feature branch
git checkout -b add-new-feature

# Claude makes changes
# Claude commits: git commit -m "Add new feature"

# Claude pushes
git push -u origin add-new-feature
```

Output shows:
```
remote: Create a pull request for 'add-new-feature' on GitHub by visiting:
remote:      https://github.com/greogory/hibp-checker/pull/new/add-new-feature
```

### 2. Create the Pull Request

**Option A: Click the link** from the push output

**Option B: Use gh CLI:**
```bash
gh pr create --title "Add new feature" --body "Description of changes"
```

**Option C: Go to GitHub web:**
- Visit https://github.com/greogory/hibp-checker
- GitHub will show a banner: "add-new-feature had recent pushes"
- Click "Compare & pull request"

### 3. Review Your Changes

On the PR page:

1. Click **"Files changed"** tab
2. Review each modified file
3. Check for:
   - ✅ No sensitive data (API keys, emails, passwords)
   - ✅ Code looks correct
   - ✅ No unintended changes

### 4. Approve the PR

1. Click **"Review changes"** button (top right)
2. Optionally type a comment: "Looks good!"
3. Select **"Approve"** radio button
4. Click **"Submit review"**

You'll see: ✅ "You approved these changes"

### 5. Merge the PR

1. Go back to **"Conversation"** tab
2. **"Merge pull request"** button is now green/clickable
3. Click **"Merge pull request"** (or dropdown for squash/rebase)
4. Click **"Confirm merge"** (or "Confirm squash and merge")
5. Optionally click **"Delete branch"** to clean up

### 6. Update Your Local Repository

```bash
git checkout main
git pull origin main
git branch -d add-new-feature  # Delete local branch (safe after merge)
```

---

## Troubleshooting

### Issue: "Merge pull request" Button is Grayed Out

**Possible reasons:**

1. **No approval yet**
   - Solution: Click "Files changed" → "Review changes" → "Approve" → "Submit review"

2. **Checks are failing**
   - Look for ❌ next to "Some checks were not successful"
   - Click "Details" to see what failed
   - Fix the issue and push to the PR branch

3. **Conversations not resolved**
   - If you left comments, mark them as resolved
   - Click "Resolve conversation" under each comment thread

4. **Missing required signatures**
   - Ensure commits are GPG-signed
   - Re-sign if needed: `git rebase --exec 'git commit --amend --no-edit -n -S' main`

### Issue: "Cannot approve your own PR"

**Reason:** "Do not allow bypassing the above settings" is enabled

**Solution:**
1. Go to branch protection settings
2. Find "Do not allow bypassing the above settings"
3. **Uncheck** this option
4. Save changes

For solo projects, you **need to approve your own PRs**. This setting should be disabled.

### Issue: "Review required, but there are no reviewers"

**This is normal!** You are the reviewer.

**Solution:**
1. Go to the PR
2. Click "Files changed"
3. Click "Review changes"
4. Select "Approve"
5. Submit review

You don't need to explicitly add yourself as a reviewer. Just approve.

### Issue: Accidentally Pushed Directly to Main

If branch protection is properly set up, this should be impossible. But if it happens:

**GitHub rejects the push:**
```
remote: error: GH013: Repository rule violations found for refs/heads/main
```

**Solution:** Use the correct workflow (create branch → PR → approve → merge)

---

## Quick Reference Card

### PR Approval Checklist

- [ ] PR created (branch pushed, link clicked)
- [ ] Changes reviewed (Files changed tab)
- [ ] No sensitive data exposed
- [ ] Code quality acceptable
- [ ] Review submitted (Approve selected)
- [ ] Checks passed (green checkmarks)
- [ ] Conversations resolved (if any)
- [ ] PR merged (Merge pull request clicked)
- [ ] Branch deleted (optional cleanup)
- [ ] Local main updated (git pull)

### Common Commands

```bash
# Create feature branch
git checkout -b feature-name

# Make changes and commit
git add .
git commit -m "description"

# Push and create PR
git push -u origin feature-name
gh pr create --title "Title" --body "Description"

# View PRs
gh pr list

# Merge PR (after approval via web)
gh pr merge PR_NUMBER --squash --delete-branch

# Update local main
git checkout main
git pull origin main
```

### Important URLs

- **Your PRs**: https://github.com/greogory/hibp-checker/pulls
- **Branch Settings**: https://github.com/greogory/hibp-checker/settings/branches
- **Security Settings**: https://github.com/greogory/hibp-checker/settings/security_analysis

---

## Best Practices

### For Solo Developers

1. **Always use feature branches** - Never work directly on main
2. **Self-review every PR** - Catch mistakes before merging
3. **Write descriptive PR titles** - Future you will thank you
4. **Use squash and merge** - Keeps git history clean
5. **Delete branches after merge** - Reduces clutter

### For Code Reviews

When reviewing your own code:

✅ **Do:**
- Read through all changes carefully
- Check for sensitive data (API keys, emails)
- Verify tests pass (if you have them)
- Ensure documentation is updated
- Look for TODO/FIXME comments

❌ **Don't:**
- Rush through the review
- Approve without reading changes
- Skip checking for security issues

---

## Summary

**Setting up approvals:**
1. Go to https://github.com/greogory/hibp-checker/settings/branches
2. Edit rule for `main`
3. Enable "Require a pull request before merging"
4. Set "Required approvals" to `1`
5. **DO NOT** enable "Do not allow bypassing the above settings"
6. Save changes

**Approving PRs:**
1. Open PR in GitHub
2. Click "Files changed"
3. Review changes
4. Click "Review changes"
5. Select "Approve"
6. Click "Submit review"
7. Go to "Conversation" tab
8. Click "Merge pull request"

**You can and should approve your own PRs as a solo developer!**

---

**Last Updated:** 2025-11-07
**Repository:** hibp-checker
