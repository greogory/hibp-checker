# GitHub Release Instructions for v2.3.0

## Release Artifacts Created ✅

All release artifacts have been created and are ready for GitHub:

### Git Commits & Tags
- ✅ Release commit: `83e0276` - "Release v2.3.0 - Web Dashboard"
- ✅ Annotated tag: `v2.3.0` with full release notes
- ✅ 18 files changed, 2,050+ lines added

### Release Archives
- ✅ `hibp-checker-v2.3.0.tar.gz` (117 KB) - Linux/macOS archive
- ✅ `hibp-checker-v2.3.0.zip` (142 KB) - Windows archive
- ✅ `hibp-checker-v2.3.0.sha256` - Checksums for verification

### Checksums (SHA256)
```
26e21ec4372714b596a9086eba9d9e067e1400176e0942ceafc0832938160985  hibp-checker-v2.3.0.tar.gz
ee30bf4f5310dbaa424694cc337058abfc519026d54046fc134a4826e89474ca  hibp-checker-v2.3.0.zip
```

## Next Steps to Publish on GitHub

### 1. Push to GitHub

First, push the commit and tag to GitHub:

```bash
cd <project-directory>

# Push the commit
git push origin main

# Push the tag
git push origin v2.3.0
```

### 2. Create GitHub Release

#### Option A: Using GitHub Web Interface (Recommended)

1. Go to your repository: https://github.com/greogory/hibp-checker
2. Click on "Releases" in the right sidebar
3. Click "Draft a new release"
4. Fill in the release form:

   **Tag version:** `v2.3.0` (select from dropdown)

   **Release title:** `v2.3.0 - Web Dashboard`

   **Description:** Use the content from `RELEASE_NOTES_v2.3.0.md`

5. Attach the release files:
   - Upload `hibp-checker-v2.3.0.tar.gz`
   - Upload `hibp-checker-v2.3.0.zip`
   - Upload `hibp-checker-v2.3.0.sha256`

6. Check "Set as the latest release"
7. Click "Publish release"

#### Option B: Using GitHub CLI

If you have `gh` CLI installed:

```bash
# Create release with files
gh release create v2.3.0 \
  --title "v2.3.0 - Web Dashboard" \
  --notes-file RELEASE_NOTES_v2.3.0.md \
  hibp-checker-v2.3.0.tar.gz \
  hibp-checker-v2.3.0.zip \
  hibp-checker-v2.3.0.sha256
```

### 3. Update Docker Image (Optional)

If you're using GitHub Container Registry:

```bash
# Build multi-platform image
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/greogory/hibp-checker:2.3.0 \
  --tag ghcr.io/greogory/hibp-checker:latest \
  --push \
  .
```

### 4. Verify Release

After publishing, verify:

- ✅ Release appears on GitHub releases page
- ✅ All artifacts are downloadable
- ✅ Tag is visible in repository
- ✅ Latest release badge is updated
- ✅ Docker image is available (if applicable)

## Release Announcement Template

### For GitHub Release Description

Use the content from `RELEASE_NOTES_v2.3.0.md` as the release description.

### For Social Media / Announcements

```
🎉 HIBP Checker v2.3.0 is here!

New in this release:
📊 Web Dashboard for viewing breach reports
🌍 Cross-platform support (Linux, Windows, macOS)
📱 Mobile-responsive design
🔄 Auto-refresh & real-time stats

Download: https://github.com/greogory/hibp-checker/releases/tag/v2.3.0

#cybersecurity #privacy #opensource
```

## Rollback Instructions (If Needed)

If you need to rollback this release:

```bash
# Delete remote tag
git push --delete origin v2.3.0

# Delete local tag
git tag -d v2.3.0

# Revert commit (if needed)
git revert 83e0276

# Push revert
git push origin main
```

## Post-Release Checklist

After publishing the release:

- [ ] Release is visible on GitHub
- [ ] All artifacts are downloadable
- [ ] README badges are updated
- [ ] Docker image is tagged (if applicable)
- [ ] Release announcement posted
- [ ] Documentation is accurate
- [ ] Issue tracker is updated
- [ ] Changelog is linked from release

## Release Statistics

**Release**: v2.3.0
**Date**: November 7, 2025
**Commit**: 83e0276dad3afb5262c5fd8c08a8493cfaddff44
**Files Changed**: 18
**Lines Added**: 2,050+
**Lines Removed**: 5
**New Files**: 13
**Modified Files**: 5

**Key Additions**:
- Web dashboard (1,500+ lines)
- Cross-platform scripts
- Comprehensive documentation
- Docker enhancements
- Systemd integration

## Support Information

**Documentation**:
- Release Notes: `RELEASE_NOTES_v2.3.0.md`
- Changelog: `CHANGELOG.md`
- Dashboard Guide: `DASHBOARD_GUIDE.md`
- Main README: `README.md`

**Contact**:
- GitHub Issues: https://github.com/greogory/hibp-checker/issues
- Email: gjbr@pm.me

---

**Created**: November 7, 2025
**Status**: ✅ Ready for GitHub Release
**Next Step**: Push to GitHub and create release
