# GPG Commit Signing Setup Guide

This guide helps you set up GPG signing for your commits so GitHub shows them as "Verified".

## Current Status

✅ GPG key exists: `2BDA30A9F34F8922`
✅ Git configured to use GPG key
✅ Automatic commit signing enabled

⚠️ **Action Required:** Add GPG key to GitHub

---

## Step 1: Copy Your GPG Public Key

Your GPG public key is:

```
-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEZ3LgKxYJKwYBBAHaRw8BAQdAu9Mpu5Fo8h/Xb7m32o0D1dKzaKooeeAykpGu
Q+hJ+sO0EkJvc2NvIDxnamJyQHBtLm1lPoiZBBMWCgBBFiEEmUDnl5BlNfs5r7Ye
K9owqfNPiSIFAmdy4CsCGwMFCQWjmoAFCwkIBwICIgIGFQoJCAsCBBYCAwECHgcC
F4AACgkQK9owqfNPiSKBmQEAp4UkZmo6LQkVTrzreGyKAoftSDbR1QyQHAtpREhv
aKgA/jl6cFL+vDoaFsVRzzqbuGOsI35vdXxgM5uJ9vkRkj0LuDgEZ3LgKxIKKwYB
BAGXVQEFAQEHQFZDcGEoMQsGrkzYLEZvt6ZMebaNFdKL9+vWY2paQV4eAwEIB4h+
BBgWCgAmFiEEmUDnl5BlNfs5r7YeK9owqfNPiSIFAmdy4CsCGwwFCQWjmoAACgkQ
K9owqfNPiSI8yQEA9usy+bg9XkhGDlxJp16TLwuzo51YeiSjRDd4g9uX7ygA/AmB
RcGMj2zeAKfqGv3ue0+w7RoGirvGAZdOIDU+PDMG
=aXBn
-----END PGP PUBLIC KEY BLOCK-----
```

**Or generate it again:**
```bash
gpg --armor --export 2BDA30A9F34F8922
```

---

## Step 2: Add GPG Key to GitHub

### Via Web Interface (Easiest)

1. **Go to GitHub GPG Keys Settings:**
   - Direct link: https://github.com/settings/gpg/new
   - Or navigate: GitHub → Settings → SSH and GPG keys → New GPG key

2. **Add the Key:**
   - Title: `CachyOS Main Key` (or any name you prefer)
   - Key: Paste the entire public key block (from BEGIN to END)
   - Click "Add GPG key"

3. **Verify:**
   - The key should appear in your GPG keys list
   - Key ID: `2BDA30A9F34F8922`
   - Email: `gjbr@pm.me`

### Via Command Line (Alternative)

```bash
# Copy key to clipboard (if xclip installed)
gpg --armor --export 2BDA30A9F34F8922 | xclip -selection clipboard

# Or save to file
gpg --armor --export 2BDA30A9F34F8922 > ~/my-gpg-key.pub

# Then upload via web interface
```

---

## Step 3: Configure Git (Already Done ✅)

Your git is already configured with:

```bash
# Global GPG key
git config --global user.signingkey 2BDA30A9F34F8922

# Automatic signing enabled
git config --global commit.gpgsign true
```

**Verify configuration:**
```bash
git config --get user.signingkey
git config --get commit.gpgsign
```

---

## Step 4: Test Signed Commit

Let's test that signing works:

```bash
cd ~/claude-archive/projects/hibp-project/

# Make a test commit
echo "# Test" >> test-signing.txt
git add test-signing.txt
git commit -m "Test GPG signing"

# Verify signature
git log --show-signature -1
```

**Expected output:**
```
gpg: Signature made ...
gpg: Good signature from "Bosco <gjbr@pm.me>" [ultimate]
```

---

## Step 5: Re-sign Previous Commits (Optional)

If you want to sign the commits in the PR:

### Option 1: Amend Last Commit

```bash
git checkout code-scanning-analysis
git commit --amend --no-edit -S
git push -f origin code-scanning-analysis
```

### Option 2: Rebase and Sign All Commits

```bash
git checkout code-scanning-analysis
git rebase --exec 'git commit --amend --no-edit -n -S' main
git push -f origin code-scanning-analysis
```

---

## Step 6: Merge the PR

Once the GPG key is added to GitHub:

1. **Refresh the PR page:** https://github.com/greogory/hibp-checker/pull/2
2. **Commits should now show "Verified" badge**
3. **Merge the PR**

---

## Troubleshooting

### Issue: "gpg failed to sign the data"

**Solution 1: Set GPG TTY**
```bash
echo 'export GPG_TTY=$(tty)' >> ~/.zshrc
source ~/.zshrc
```

**Solution 2: Start GPG agent**
```bash
gpg-agent --daemon
```

**Solution 3: Test GPG**
```bash
echo "test" | gpg --clearsign
```

### Issue: "No secret key"

**Check key exists:**
```bash
gpg --list-secret-keys --keyid-format=long
```

**Verify git config:**
```bash
git config --get user.signingkey
```

### Issue: Commits Still Show Unverified

**Possible causes:**
1. GPG key not added to GitHub
2. Email in commit doesn't match GPG key email
3. Key expired

**Check commit email:**
```bash
git log -1 --format='%ae'
```

**Check GPG key email:**
```bash
gpg --list-keys 2BDA30A9F34F8922
```

**They must match!**

### Issue: Wrong Email in Commits

**Fix with:**
```bash
git config --global user.email "gjbr@pm.me"
```

---

## Git Configuration Summary

Current configuration:

```bash
# User info
user.name = [your name]
user.email = gjbr@pm.me

# GPG signing
user.signingkey = 2BDA30A9F34F8922
commit.gpgsign = true
```

**View all config:**
```bash
git config --global --list | grep -E "(user|gpg|sign)"
```

---

## Security Benefits

With GPG signing enabled:

✅ **Verified commits** - GitHub shows "Verified" badge
✅ **Authenticity** - Proves commits are from you
✅ **Tamper-proof** - Can't modify signed commits without breaking signature
✅ **Branch protection** - Enforces signature requirement
✅ **Trust chain** - Others can verify your identity

---

## Future Commits

All future commits will automatically be signed because:
- `commit.gpgsign = true` is set globally
- Your GPG key is configured
- Git will prompt for GPG passphrase when needed

**No extra flags needed!**

```bash
git commit -m "message"  # Automatically signed
```

---

## Quick Reference

### Export Public Key
```bash
gpg --armor --export 2BDA30A9F34F8922
```

### Sign Commit Manually
```bash
git commit -S -m "message"
```

### Verify Signature
```bash
git log --show-signature
```

### Check Key Expiry
```bash
gpg --list-keys 2BDA30A9F34F8922
```

### Extend Key Expiry (if needed)
```bash
gpg --edit-key 2BDA30A9F34F8922
> expire
> [follow prompts]
> save
```

---

## Next Steps

1. ✅ **Add GPG key to GitHub** (see Step 2)
2. **Test with a new commit**
3. **Verify "Verified" badge appears**
4. **(Optional) Re-sign PR commits**
5. **Merge PR #2**

---

**Key Information:**
- **Key ID:** `2BDA30A9F34F8922`
- **Email:** `gjbr@pm.me`
- **Expires:** 2027-12-30
- **Type:** Ed25519

---

**Last Updated:** 2025-11-07
