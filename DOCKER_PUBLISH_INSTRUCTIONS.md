# Docker Image Publishing Instructions

## Current Status

✅ **Docker image built successfully**
- Image ID: `bd230267d7ab`
- Tags: `ghcr.io/greogory/hibp-checker:2.3.2.2`, `ghcr.io/greogory/hibp-checker:latest`
- Includes: Dashboard, Flask, all v2.3.2.2 features
- Size: ~300 MB (Python 3.11-slim base)

❌ **Push failed** - Token requires `write:packages` scope

## How to Publish the Docker Image

### Option 1: Using GitHub Personal Access Token (Recommended)

1. **Create a new token with packages scope:**
   - Go to: https://github.com/settings/tokens/new
   - Select scopes:
     - ✅ `write:packages` (Upload packages to GitHub Package Registry)
     - ✅ `read:packages` (Download packages from GitHub Package Registry)
     - ✅ `delete:packages` (Delete packages from GitHub Package Registry)
   - Generate token and save it

2. **Login to GitHub Container Registry:**
   ```bash
   echo "YOUR_TOKEN_HERE" | docker login ghcr.io -u greogory --password-stdin
   ```

3. **Push the images:**
   ```bash
   cd <project-directory>

   # Push v2.3.2.2 tag
   docker push ghcr.io/greogory/hibp-checker:2.3.2.2

   # Push latest tag
   docker push ghcr.io/greogory/hibp-checker:latest
   ```

### Option 2: Using GitHub Actions (Automated)

The repository already has a GitHub Actions workflow that can build and push Docker images. To use it:

1. **Set up repository secrets:**
   - Go to: https://github.com/greogory/hibp-checker/settings/secrets/actions
   - Add `GHCR_TOKEN` with a PAT that has `write:packages` scope

2. **Trigger the workflow:**
   - The workflow will automatically build and push on new releases
   - Or manually trigger from Actions tab

### Option 3: Rebuild and Push Locally

If you've lost the local image:

```bash
cd <project-directory>

# Rebuild
docker build -t ghcr.io/greogory/hibp-checker:2.3.2.2 \
             -t ghcr.io/greogory/hibp-checker:latest .

# Login with proper token
echo "YOUR_TOKEN" | docker login ghcr.io -u greogory --password-stdin

# Push
docker push ghcr.io/greogory/hibp-checker:2.3.2.2
docker push ghcr.io/greogory/hibp-checker:latest
```

## Verify Publication

After pushing, verify the image is available:

```bash
# Pull the image
docker pull ghcr.io/greogory/hibp-checker:2.3.2.2

# Check it works
docker run --rm ghcr.io/greogory/hibp-checker:2.3.2.2 python3 --version

# Test dashboard
docker run --rm -p 5000:5000 \
  -v $(pwd)/reports:/app/reports:ro \
  ghcr.io/greogory/hibp-checker:2.3.2.2 \
  python3 dashboard/app.py
```

## Package Visibility

After pushing, make the package public:

1. Go to: https://github.com/users/greogory/packages/container/hibp-checker/settings
2. Change visibility to "Public"
3. Link to repository: https://github.com/greogory/hibp-checker

## Multi-Platform Build (Optional)

For ARM64 support (Apple Silicon, Raspberry Pi):

```bash
# Install buildx
docker buildx create --name multiplatform --use

# Build and push multi-platform
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/greogory/hibp-checker:2.3.2.2 \
  -t ghcr.io/greogory/hibp-checker:latest \
  --push \
  .
```

## Testing the Published Image

Once published, users can:

```bash
# Pull and run
docker run --rm ghcr.io/greogory/hibp-checker:latest

# Run dashboard
docker-compose --profile dashboard up -d

# Run a check
docker run --rm \
  -e HIBP_API_KEY="your-key" \
  ghcr.io/greogory/hibp-checker:2.3.2.2 \
  python3 hibp_comprehensive_checker.py -e test@example.com
```

## Troubleshooting

### Permission Denied
- Ensure token has `write:packages` scope
- Verify you're logged in: `docker login ghcr.io`
- Check token hasn't expired

### Image Not Found
- Wait a few minutes after pushing (registry indexing)
- Verify package visibility is set to "Public"
- Check package exists: https://github.com/users/greogory/packages

### Size Too Large
- Current image: ~300 MB (reasonable for Python + Flask)
- To reduce: Use alpine base, multi-stage build
- For now: size is acceptable

## Current Image Details

```
Repository: ghcr.io/greogory/hibp-checker
Tags: 2.3.2.2, latest
Base: python:3.11-slim
Architecture: linux/amd64
Contents:
  - HIBP checker script
  - Dashboard application
  - Flask web server
  - All dependencies
  - Cross-platform scripts
```

## Next Steps

1. Create PAT with `write:packages` scope
2. Login to GHCR with the token
3. Push both tags (2.3.2.2 and latest)
4. Verify images are available
5. Update package visibility to public
6. Test pulling and running

---

**Built**: November 8, 2025
**Version**: 2.3.2.2
**Status**: ✅ Built locally, ⏳ Awaiting publish
**Action Required**: Token with `write:packages` scope needed
