# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

## [2.3.3] - 2026-01-14

### Added
- CodeQL exclusion config (`.github/codeql/codeql-config.yml`) to suppress false positive alerts:
  - `py/weak-cryptographic-algorithm` - SHA1 required by HIBP API protocol
  - `py/path-injection` - `safe_path_join()` validation exists
  - `py/clear-text-logging-sensitive-data` - `redact_sensitive()` in use

### Changed
- Synced all documentation version references to 2.3.2.2
- Updated Dockerfile version label
- Updated DOCKER.md and DOCKER_PUBLISH_INSTRUCTIONS.md

## [2.3.2.2] - 2026-01-13

### Changed
- Test release to verify automatic badge updates in `/git-release` workflow

## [2.3.2.1] - 2026-01-13

### Added
- Multi-segment version badges in README with hierarchical color scheme
- Version history table showing release progression

## [2.3.2] - 2026-01-13

### Added
- `docs/ARCHITECTURE.md` - System architecture documentation

### Changed
- Updated .gitignore with local tool config patterns (bandit, pyproject.toml, ruff)

## [2.3.1] - 2026-01-09

### Security
- Fixed path traversal vulnerabilities in dashboard/app.py (CodeQL finding)
- Fixed sensitive data exposure in logging with `redact_sensitive()` helper
- Added request timeouts (30s) to prevent hanging on slow/unresponsive endpoints
- Updated urllib3 to 2.6.3 for CVE-2026-21441
- Added `usedforsecurity=False` to SHA1 calls (HIBP API requirement, not cryptographic)
- Hardened systemd service with `ProtectSystem=strict`, `ProtectHome=read-only`

### Added
- CodeQL semantic code analysis workflow (`.github/workflows/codeql.yml`)
- Python security and quality workflow with pip-audit, bandit, ruff
- Daily automated security scans (upgraded from weekly)

### Changed
- Replaced wildcard imports in test fixtures with explicit imports
- Added `__all__` declaration to test fixtures for proper re-exports
- Pinned Python 3.14.2 via pyenv for reproducible builds
- Updated documentation version references from 2.0.0 to 2.3.0

### Fixed
- GitHub workflow permissions (added `contents: read`)
- Test artifact patterns added to .gitignore

## [2.3.0] - 2025-12-29

### Added
- Comprehensive pytest test suite with 203+ tests achieving 85%+ coverage
- HEALTHCHECK instruction in Dockerfile for container health monitoring
- Testing dependencies: pytest, pytest-cov, pytest-mock, responses

### Changed
- Removed obsolete `version` field from docker-compose.yml and docker-compose.scheduled.yml (deprecated in Compose v2)
- Added version label (`org.opencontainers.image.version`) to Dockerfile metadata

### Fixed
- Security: pinned werkzeug>=3.1.4 to address CVE-2025-66221
- Code quality improvements: removed trailing whitespace across multiple files
- Added missing docstrings to dashboard/bitwarden_checker.py classes

## [2.2.3] - 2025-12-27

### Changed
- Updated README version badges to match VERSION file (2.2.2 → now 2.2.3)

### Fixed
- Added `.exit*` pattern to .gitignore to exclude session timestamp files

## [2.2.2] - 2025-12-24

### Added
- `bw-session-setup.sh` - Helper script to set up persistent Bitwarden session
- Bitwarden session file support (`~/.bw_session`) for dashboard integration

### Changed
- **Generic Installation Paths**: All hardcoded paths replaced with dynamic detection
  - Systemd services now use `HIBP_PROJECT_DIR` placeholder (auto-configured by setup script)
  - Shell scripts use `SCRIPT_DIR` for self-location
  - Documentation updated to use `<project-directory>` placeholder
- `scripts/setup-systemd.sh` now auto-configures paths and installs dashboard service
- `bitwarden_checker.py` reads BW_SESSION from `~/.bw_session` as fallback
- `start-dashboard.sh` and `launch-dashboard.sh` source BW_SESSION from file

### Fixed
- Dashboard now works for any user regardless of installation location
- Bitwarden integration works without manually exporting BW_SESSION each session

### Documentation
- All documentation updated to use generic paths instead of hardcoded locations
- Added instructions for `bw-session-setup.sh` usage

## [2.2.0] - 2025-12-24

### Added
- **Bitwarden Password Audit in Dashboard**
  - New "Bitwarden" tab in web UI for password health checks
  - "Run Password Check" button to trigger `bw-hibp-stream.py`
  - Real-time progress indicator with shimmer animation
  - Results display with summary stats (Safe, Compromised, Critical, Total)
  - Compromised passwords list sorted by breach count with risk badges
  - Historical report storage (last 10 checks preserved)
  - Prerequisites check with helpful error messages

### Technical
- New `bitwarden_checker.py` module for subprocess management and task tracking
- 5 new API endpoints for Bitwarden integration:
  - `GET /api/bitwarden/status` - Check prerequisites
  - `POST /api/bitwarden/check` - Start password check
  - `GET /api/bitwarden/task/<id>` - Poll task status
  - `GET /api/bitwarden/reports` - List saved reports
  - `GET /api/bitwarden/report/<filename>` - Get report details

## [2.1.0] - 2025-12-24

### Added
- `bw-hibp-stream.py` - Streaming Bitwarden password checker
  - Reads vault items directly from `bw list items` via stdin
  - Passwords never written to disk (memory-only processing)
  - Multiple report formats: text, JSON, CSV
  - Risk level classification: Critical, High, Medium, Low
  - `--compromised-only` flag to filter results
  - Rate-limited API requests (100ms delay)

### Documentation
- Added Bitwarden Password Checking section to README
- Documented both streaming and file-based approaches

## [2.0.1] - 2025-11-24

### Added
- New utility scripts:
  - `check-bitwarden-passwords.py` - Direct Bitwarden vault password checking
  - `check-passwords.py` - Standalone password breach checker
  - `verify-dns.sh` - DNS verification utility
  - `launch-dashboard.sh` - Quick dashboard launcher
- Dashboard archive template (`dashboard/templates/archive.html`)
- Docker and GitHub release documentation

### Changed
- **Systemd Timer Improvements**:
  - Changed default schedule from 3 AM to 2 AM
  - Added `OnBootSec=15min` - runs 15 minutes after boot if scheduled time was missed
  - Updated systemd service paths from `~/claude-archive/projects/hibp-project` to `/raid0/ClaudeCodeProjects/hibp-project`
  - Fixed `ReadWritePaths` to use correct project location
- Enhanced `.gitignore` to exclude release artifacts

### Fixed
- Systemd service template paths now reference correct project directory
- Timer configuration more resilient to system downtime

### Documentation
- Added `DOCKER_PUBLISH_INSTRUCTIONS.md` for Docker image publishing workflow
- Added `GITHUB_RELEASE_INSTRUCTIONS.md` for release creation process

## [2.0.0] - 2025-11-07

### 🎉 Major New Features

#### Web Dashboard
- **NEW**: Modern web-based dashboard for viewing breach reports and logs
- Real-time statistics display (total scans, breaches, password exposures)
- Interactive report browser with color-coded severity indicators
- Built-in log viewer for workflow, systemd, and error logs
- Auto-refresh functionality (updates every 60 seconds)
- Download reports directly from the browser
- Mobile-responsive design
- Secure localhost-only access (127.0.0.1:5000)

### Added

#### Dashboard Components
- Flask-based backend API (`dashboard/app.py`)
- Single-page HTML/CSS/JS frontend (`dashboard/templates/index.html`)
- Systemd service for Linux auto-start (`dashboard/systemd/hibp-dashboard.service`)
- Cross-platform startup scripts:
  - Linux: `dashboard/start-dashboard.sh`
  - Windows: `dashboard/start-dashboard.ps1`
  - macOS: `dashboard/start-dashboard-macos.sh`
- Dashboard documentation (`dashboard/README.md`, `DASHBOARD_GUIDE.md`)

#### Docker Support
- Dashboard Docker Compose profile
- Updated Dockerfile to include dashboard
- Multi-platform Docker image support (linux/amd64, linux/arm64)

#### Documentation
- Complete dashboard setup guides for all platforms
- Quick reference guide (`DASHBOARD_GUIDE.md`)
- Updated main README with dashboard sections
- Platform-specific installation instructions

### Changed

- Updated Docker Compose to v2.0 format with dashboard service
- Enhanced Dockerfile with Flask and dashboard dependencies
- Restructured project to include dashboard as first-class feature
- Updated README with dashboard-first approach in Usage section

### Technical Details

#### Dependencies
- Added Flask >= 2.0.0 for web framework
- Added requests >= 2.25.0 (already required)
- Created `requirements.txt` for easier installation

#### File Structure
```
dashboard/
├── app.py                          # Flask backend API
├── templates/
│   └── index.html                  # Dashboard UI
├── static/
│   ├── css/
│   └── js/
├── systemd/
│   └── hibp-dashboard.service      # Linux systemd service
├── start-dashboard.sh              # Linux startup script
├── start-dashboard.ps1             # Windows PowerShell script
├── start-dashboard-macos.sh        # macOS startup script
└── README.md                       # Dashboard documentation
```

#### API Endpoints
- `GET /` - Main dashboard interface
- `GET /api/stats` - Dashboard statistics
- `GET /api/reports` - List all breach reports
- `GET /api/report/<filename>` - Get detailed report
- `GET /api/logs/<type>` - Get log content (workflow, systemd, error)
- `GET /download/<filename>` - Download a report file

### Security

- Dashboard runs on localhost only (127.0.0.1) - no external network access
- Read-only access to reports and logs
- Systemd security hardening (PrivateTmp, NoNewPrivileges)
- No authentication required (localhost-only access model)

### Platform Support

#### Linux
- Native Flask application
- Systemd service for auto-start on boot
- Works with existing HIBP checker automation

#### Windows
- Docker-based deployment (recommended)
- PowerShell startup script included
- WSL2 support for native installation

#### macOS
- Docker-based deployment (recommended)
- Native bash script for local installation
- Homebrew-compatible

### Upgrade Instructions

#### From v1.x to v2.0

1. Pull the latest code:
   ```bash
   cd ~/hibp-checker
   git pull
   ```

2. Install dashboard dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Start the dashboard:
   ```bash
   # Linux - systemd
   cp dashboard/systemd/hibp-dashboard.service ~/.config/systemd/user/
   systemctl --user daemon-reload
   systemctl --user enable --now hibp-dashboard.service

   # Or manual start
   cd dashboard
   ./start-dashboard.sh
   ```

4. Access dashboard at http://127.0.0.1:5000

#### Docker Users

Update your docker-compose.yml and run:
```bash
docker-compose pull
docker-compose --profile dashboard up -d
```

### Breaking Changes

None. All existing functionality remains unchanged. Dashboard is an additive feature.

### Known Issues

None at this time.

### Contributors

- Bosco (@greogory) - Initial dashboard implementation

---

## [1.0.0] - 2025-11-07

### Initial Release

- Comprehensive HIBP breach checking
- Password exposure detection
- Stealer log mining
- Critical site identification
- Pwned password checking
- Multi-format reporting (JSON, CSV, text)
- Email list support
- Automated scheduling (systemd timers)
- Docker support
- Cross-platform compatibility

---

**Full Changelog**: https://github.com/greogory/hibp-checker/compare/v1.0.0...v2.3.2
