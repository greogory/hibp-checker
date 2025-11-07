# Automatic PR Approval & Merge Setup

---

## ⚡ Powered by Have I Been Pwned

This tool uses data from **[Have I Been Pwned](https://haveibeenpwned.com)** by Troy Hunt, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

## Overview

This guide sets up **automatic approval and merging** for Pull Requests created by you (the repo owner). This eliminates the redundant step of manually approving your own changes.

### Why Auto-Approval Makes Sense for Solo Projects

As the sole maintainer:
- ✅ You already tested the changes before committing
- ✅ You reviewed the code while writing it
- ✅ Manual self-approval is redundant and slows you down
- ✅ Branch protection still prevents accidental direct pushes
- ✅ Security checks still run automatically
- ✅ You can still review PRs before they auto-merge if needed

## How It Works

When you push a branch and create a PR:

1. **Security checks run** (your existing `security-checks.yml` workflow)
2. **Auto-approval runs** (approves PRs created by you)
3. **Auto-merge queues** (waits for all checks to pass)
4. **PR merges automatically** (once checks are green)
5. **Branch deletes automatically** (cleanup)

**Total time**: ~30-60 seconds after push (depending on CI duration)

---

## Setup Instructions

### Step 1: Add GitHub Actions Workflows

Two workflow files have been created:

1. **`.github/workflows/auto-approve.yml`** - Automatically approves your PRs
2. **`.github/workflows/auto-merge.yml`** - Automatically merges approved PRs

These files are already in your repository.

### Step 2: Enable GitHub Actions Permissions

GitHub Actions needs permission to approve and merge PRs.

**Go to**: https://github.com/greogory/hibp-checker/settings/actions

Under **"Workflow permissions"**:

1. Select: ☑️ **"Read and write permissions"**
2. Enable: ☑️ **"Allow GitHub Actions to create and approve pull requests"**
3. Click **"Save"**

### Step 3: Enable Auto-Merge Feature (Repository Setting)

**Go to**: https://github.com/greogory/hibp-checker/settings

Scroll down to **"Pull Requests"** section:

1. Enable: ☑️ **"Allow auto-merge"**
2. Optionally enable: ☑️ **"Automatically delete head branches"**

### Step 4: Configure Branch Protection (Keep Existing Rules)

**Go to**: https://github.com/greogory/hibp-checker/settings/branches

Your existing branch protection for `main` should have:

- ☑️ **Require a pull request before merging**
  - Required approvals: `1`
- ☑️ **Require status checks to pass before merging**
  - Select: `security-scan` (from security-checks.yml)
  - ☑️ **Require branches to be up to date before merging**
- ☑️ **Require conversation resolution before merging**
- ☑️ **Require signed commits** (you already have this)
- ☑️ **Do not allow force pushes**
- ☑️ **Do not allow deletions**

**IMPORTANT**:
- ☐ **Do NOT enable** "Do not allow bypassing the above settings"
  - This would prevent the auto-approval from working

### Step 5: Push the Workflow Files

The workflow files need to be committed and pushed to enable them.

**Note**: You'll need the `workflow` scope in your GitHub token:

```bash
# Grant workflow scope
gh auth refresh -h github.com -s workflow
```

Then:

```bash
cd ~/claude-archive/projects/hibp-project

# Create a branch for this change
git checkout -b setup-auto-approval

# Add the workflow files
git add .github/workflows/auto-approve.yml
git add .github/workflows/auto-merge.yml
git add AUTO_APPROVAL_SETUP.md

# Commit
git commit -m "Add automatic PR approval and merge workflows"

# Push and create PR
git push -u origin setup-auto-approval
gh pr create --title "Setup Automatic PR Approval" \
  --body "Adds GitHub Actions workflows to automatically approve and merge PRs created by repo owner."
```

**For this first PR**, you'll need to manually approve and merge it (since the auto-approval workflow isn't active yet). After this, all future PRs will be automatic.

---

## How to Use (After Setup)

### Making Changes (Same as Before)

```bash
# 1. Create feature branch
git checkout -b new-feature

# 2. Make your changes
echo "changes" >> file.txt
git add .
git commit -m "Add new feature"

# 3. Push branch
git push -u origin new-feature

# 4. Create PR
gh pr create --title "Add new feature" --body "Description"
```

### What Happens Automatically

```
1. PR created                    [You]
   ↓
2. Security checks run           [GitHub Actions - 30s]
   ↓
3. PR auto-approved              [GitHub Actions - instant]
   ↓
4. Checks pass ✅                [GitHub Actions]
   ↓
5. PR auto-merged                [GitHub Actions - instant]
   ↓
6. Branch deleted                [GitHub Actions - instant]
```

**Total time**: ~30-60 seconds from push to merge

### Updating Local Main

After the PR auto-merges:

```bash
git checkout main
git pull origin main
git branch -d new-feature  # Delete local branch
```

---

## Workflow Details

### Auto-Approve Workflow

**File**: `.github/workflows/auto-approve.yml`

**Triggers**: When a PR is opened, synchronized (new commits), or reopened

**What it does**:
- Checks if PR author is the repo owner (you)
- If yes, automatically approves the PR
- If no (future collaborators), requires manual approval

**Key feature**: Only auto-approves PRs created by you

### Auto-Merge Workflow

**File**: `.github/workflows/auto-merge.yml`

**Triggers**: When a PR is opened or approved

**What it does**:
- Checks if PR author is the repo owner
- Enables auto-merge with squash strategy
- PR will merge automatically once all checks pass
- Deletes branch after merge

**Safety**: Waits for all required checks (security-scan) to pass

---

## Safety Features

Even with auto-approval, you still have:

### ✅ Security Checks (Always Run)

Your `security-checks.yml` workflow still runs and checks for:
- Hardcoded API keys
- .gitignore integrity
- Sensitive data patterns
- Python dependency vulnerabilities
- Accidentally committed reports
- Dangerous logging patterns

**If checks fail, PR won't merge** (even if approved)

### ✅ Branch Protection

- Direct pushes to main blocked
- Force pushes blocked
- Branch deletion blocked
- GPG signatures required

### ✅ Manual Override

You can still:
- View PRs before they merge: https://github.com/greogory/hibp-checker/pulls
- Comment on PRs
- Request changes (blocks auto-merge)
- Manually close PRs without merging

### ✅ Owner-Only Auto-Approval

Only PRs created by `greogory` (you) are auto-approved. Future collaborators would need manual approval.

---

## Disabling Auto-Approval (If Needed)

### Temporary Disable

If you want to review a specific PR manually:

1. Go to the PR
2. Comment: `/no-merge` or similar
3. Close the PR if needed
4. The workflow only runs on open PRs

### Permanent Disable

Delete or disable the workflow files:

```bash
# Option 1: Delete workflows
rm .github/workflows/auto-approve.yml
rm .github/workflows/auto-merge.yml
git commit -m "Disable auto-approval"
git push

# Option 2: Disable in GitHub UI
# Go to: Actions → Select workflow → Disable workflow
```

---

## Troubleshooting

### Issue: Workflows Not Running

**Check**: https://github.com/greogory/hibp-checker/settings/actions

Ensure:
- Workflows are enabled (not disabled)
- "Read and write permissions" is selected
- "Allow GitHub Actions to create and approve pull requests" is enabled

### Issue: PR Not Auto-Approving

**Possible causes**:

1. **Workflow files not in main branch**
   - Solution: Merge the initial PR that adds the workflows

2. **Wrong permissions**
   - Go to repository settings → Actions
   - Enable "Allow GitHub Actions to create and approve pull requests"

3. **PR not created by owner**
   - Check: Is the PR author `greogory`?
   - The workflow only runs for owner PRs

### Issue: PR Approved But Not Merging

**Possible causes**:

1. **Auto-merge not enabled**
   - Go to: https://github.com/greogory/hibp-checker/settings
   - Enable "Allow auto-merge"

2. **Checks failing**
   - Look for ❌ in the PR
   - Fix the failing check
   - Push to the PR branch

3. **Conversations not resolved**
   - Resolve any comment threads
   - Or disable "Require conversation resolution" in branch protection

### Issue: "workflow" Scope Error

When pushing workflow files:

```
refusing to allow an OAuth App to create or update workflow without `workflow` scope
```

**Solution**:
```bash
gh auth refresh -h github.com -s workflow
```

Follow the prompts to authorize the workflow scope.

---

## Comparison: Manual vs Auto-Approval

### Before (Manual Approval)

```bash
git push origin feature-branch
gh pr create --title "Feature" --body "Description"

# Then you must:
# 1. Go to GitHub web interface
# 2. Open the PR
# 3. Click "Files changed"
# 4. Click "Review changes"
# 5. Select "Approve"
# 6. Click "Submit review"
# 7. Click "Merge pull request"
# 8. Click "Confirm squash and merge"

git checkout main
git pull
```

**Time**: ~2-3 minutes (manual clicks)

### After (Auto-Approval)

```bash
git push origin feature-branch
gh pr create --title "Feature" --body "Description"

# Wait 30-60 seconds (automatic)

git checkout main
git pull
```

**Time**: 30-60 seconds (fully automated)

**Saved**: 1-2 minutes per PR, zero manual clicks

---

## Alternative: CLI-Only Auto-Merge

If you prefer not to use GitHub Actions, you can use `gh` CLI with auto-merge:

```bash
# Create PR with auto-merge enabled
gh pr create --title "Feature" --body "Description" --auto-merge

# Or enable auto-merge on existing PR
gh pr merge PR_NUMBER --auto --squash --delete-branch
```

**Limitations**:
- Still requires manual approval (unless you use the GitHub Actions workflow)
- Doesn't auto-approve, only auto-merges after approval

---

## Best Practices with Auto-Approval

### 1. Test Locally Before Pushing

Since PRs auto-merge, make sure to test your changes:

```bash
# Run tests
./hibp_workflow.sh check

# Verify changes
git diff main
```

### 2. Use Descriptive PR Titles

You won't be reviewing in the UI, so make titles clear:

```bash
# Good
gh pr create --title "Add email validation to workflow script"

# Bad
gh pr create --title "Update"
```

### 3. Monitor GitHub Actions

Check occasionally: https://github.com/greogory/hibp-checker/actions

Ensure workflows are passing.

### 4. Review Failed Checks Immediately

If a security check fails:
1. PR won't auto-merge (safe!)
2. Check the error: `gh pr checks`
3. Fix and push to the PR branch

---

## Summary

### Setup Checklist

- [ ] Add workflow files (.github/workflows/auto-approve.yml and auto-merge.yml)
- [ ] Enable "Read and write permissions" in Actions settings
- [ ] Enable "Allow GitHub Actions to create and approve pull requests"
- [ ] Enable "Allow auto-merge" in repository settings
- [ ] Verify branch protection requires 1 approval
- [ ] Verify branch protection requires security-scan check
- [ ] Do NOT enable "Do not allow bypassing the above settings"
- [ ] Grant `workflow` scope: `gh auth refresh -h github.com -s workflow`
- [ ] Push workflow files and merge initial PR manually
- [ ] Test with a sample PR

### How It Works

1. **You push** → PR created
2. **GitHub Actions** → Approves your PR automatically
3. **Security checks** → Run and must pass
4. **GitHub Actions** → Merges PR automatically
5. **You pull** → Get updated main branch

**No manual approval needed!**

### Safety

- ✅ Security checks still run
- ✅ Failed checks block merge
- ✅ Only owner PRs auto-approve
- ✅ Branch protection still active
- ✅ Can manually close PRs anytime

---

**Last Updated:** 2025-11-07
**Repository:** hibp-checker
