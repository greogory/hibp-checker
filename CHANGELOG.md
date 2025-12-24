# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

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

**Full Changelog**: https://github.com/greogory/hibp-checker/compare/v1.0.0...v2.0.0
