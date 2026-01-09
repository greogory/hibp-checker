#!/usr/bin/env python3
"""
HIBP Dashboard - Web Interface for Breach Reports
A local Flask-based dashboard to view HIBP breach reports and logs
"""

from flask import Flask, render_template, jsonify, send_file, abort
import os
import glob
import logging
from datetime import datetime
from pathlib import Path

from bitwarden_checker import BitwardenChecker

app = Flask(__name__)

# Configure logging to avoid exposing sensitive info
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal attacks.
    Only allows alphanumeric characters, underscores, hyphens, and dots.
    """
    if not filename:
        return ""
    # Remove any path components - only keep the basename
    basename = os.path.basename(filename)
    # Validate characters: only allow safe filename characters
    safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.')
    if not all(c in safe_chars for c in basename):
        return ""
    # Prevent hidden files and double extensions that could be exploited
    if basename.startswith('.') or '..' in basename:
        return ""
    return basename


def safe_path_join(base_dir: Path, filename: str) -> Path | None:
    """
    Safely join a base directory with a filename, preventing path traversal.
    Returns None if the resulting path would be outside base_dir.
    """
    sanitized = sanitize_filename(filename)
    if not sanitized:
        return None

    full_path = (base_dir / sanitized).resolve()
    base_resolved = base_dir.resolve()

    # Verify the resolved path is under the base directory
    try:
        full_path.relative_to(base_resolved)
        return full_path
    except ValueError:
        return None

# Configuration
BASE_DIR = Path(__file__).parent.parent
# XDG-compliant: reports are stored in ~/.local/share/hibp-checker/reports
XDG_DATA_HOME = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
HIBP_DATA_DIR = XDG_DATA_HOME / 'hibp-checker'
REPORTS_DIR = HIBP_DATA_DIR / 'reports'
LOGS_DIR = HIBP_DATA_DIR / 'logs'
SYSTEMD_LOG_DIR = HIBP_DATA_DIR

# Initialize Bitwarden checker
bitwarden_checker = BitwardenChecker(BASE_DIR)

def parse_text_report(filepath):
    """Parse a text-based HIBP report"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Extract summary data
        summary = {
            'filename': os.path.basename(filepath),
            'filepath': str(filepath),
            'timestamp': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
            'size': os.path.getsize(filepath),
            'total_breaches': 0,
            'password_exposures': 0,
            'stealer_logs': 0,
            'critical_sites': 0,
            'paste_exposures': 0,
            'emails_checked': []
        }

        # Parse summary section
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'Total Breaches:' in line:
                summary['total_breaches'] = int(line.split(':')[1].strip())
            elif 'Password Exposures:' in line:
                summary['password_exposures'] = int(line.split(':')[1].strip())
            elif 'Stealer Log Hits:' in line:
                summary['stealer_logs'] = int(line.split(':')[1].strip())
            elif 'Critical Sites Compromised:' in line:
                summary['critical_sites'] = int(line.split(':')[1].strip())
            elif 'Paste Exposures:' in line:
                summary['paste_exposures'] = int(line.split(':')[1].strip())
            elif line.startswith('EMAIL:'):
                email = line.replace('EMAIL:', '').strip()
                if email not in summary['emails_checked']:
                    summary['emails_checked'].append(email)

        summary['content'] = content
        # Determine severity based on breach data
        if summary['password_exposures'] > 0 or summary['critical_sites'] > 0:
            summary['severity'] = 'critical'
        elif summary['total_breaches'] > 0:
            summary['severity'] = 'warning'
        else:
            summary['severity'] = 'clean'

        return summary
    except Exception as e:
        # Log the actual error internally, but don't expose details to users
        logger.error("Error parsing report %s: %s", os.path.basename(filepath), e)
        return {
            'filename': os.path.basename(filepath),
            'error': 'Failed to parse report file',
            'severity': 'error'
        }

def get_all_reports():
    """Get all HIBP reports"""
    reports = []

    # Get text reports
    for report_file in glob.glob(str(REPORTS_DIR / '*.txt')):
        report = parse_text_report(report_file)
        reports.append(report)

    # Sort by timestamp (newest first)
    reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    return reports


def compare_reports(latest, previous):
    """Compare two reports to detect new breaches"""
    if not latest or not previous:
        return None

    latest_breaches = latest.get('total_breaches', 0)
    previous_breaches = previous.get('total_breaches', 0)

    return {
        'has_new_breaches': latest_breaches > previous_breaches,
        'breach_delta': latest_breaches - previous_breaches,
        'latest_breaches': latest_breaches,
        'previous_breaches': previous_breaches,
        'password_exposures_delta': latest.get('password_exposures', 0) - previous.get('password_exposures', 0)
    }

def get_log_content(log_type='workflow'):
    """Get log file content"""
    log_files = {
        'workflow': LOGS_DIR / 'hibp_workflow.log',
        'systemd': SYSTEMD_LOG_DIR / 'hibp-checker.log',
        'error': SYSTEMD_LOG_DIR / 'hibp-checker.error.log'
    }

    log_file = log_files.get(log_type)
    if not log_file:
        return "Invalid log type"
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                # Get last 500 lines
                lines = f.readlines()
                return ''.join(lines[-500:])
        except Exception as e:
            # Log the actual error internally, but don't expose details
            logger.error("Error reading log %s: %s", log_type, e)
            return "Error reading log file"
    return "Log file not found"

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/archive')
def archive():
    """Archive page with all reports"""
    return render_template('archive.html')

@app.route('/api/reports')
def api_reports():
    """API endpoint to get all reports"""
    reports = get_all_reports()

    # Calculate summary stats
    total_breaches = sum(r.get('total_breaches', 0) for r in reports)
    total_password_exposures = sum(r.get('password_exposures', 0) for r in reports)

    return jsonify({
        'reports': reports,
        'summary': {
            'total_reports': len(reports),
            'latest_scan': reports[0]['timestamp'] if reports else None,
            'total_breaches_found': total_breaches,
            'total_password_exposures': total_password_exposures
        }
    })

@app.route('/api/report/<filename>')
def api_report_detail(filename):
    """API endpoint to get detailed report"""
    filepath = safe_path_join(REPORTS_DIR, filename)
    if filepath is None:
        abort(400, description="Invalid filename")
    if filepath.exists():
        report = parse_text_report(filepath)
        return jsonify(report)
    return jsonify({'error': 'Report not found'}), 404

@app.route('/api/logs/<log_type>')
def api_logs(log_type):
    """API endpoint to get log content"""
    content = get_log_content(log_type)
    return jsonify({'content': content, 'type': log_type})

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    reports = get_all_reports()

    # Calculate various statistics
    stats = {
        'total_scans': len(reports),
        'latest_scan': reports[0]['timestamp'] if reports else None,
        'total_breaches': 0,
        'total_password_exposures': 0,
        'total_stealer_logs': 0,
        'total_critical_sites': 0,
        'severity_breakdown': {
            'critical': 0,
            'warning': 0,
            'clean': 0,
            'error': 0
        },
        'recent_scans': [],
        'breach_status': None,
        'status_message': 'No reports available'
    }

    if not reports:
        return jsonify(stats)

    # Compare latest with previous to detect new breaches
    if len(reports) >= 2:
        comparison = compare_reports(reports[0], reports[1])
        stats['breach_status'] = comparison

        if comparison['has_new_breaches']:
            stats['status_message'] = f"⚠️ {comparison['breach_delta']} new breach(es) detected since last scan"
        else:
            stats['status_message'] = "✅ No new breaches since last scan"
    elif len(reports) == 1:
        stats['status_message'] = f"First scan: {reports[0].get('total_breaches', 0)} breach(es) found"

    # Get latest report stats (current state)
    latest = reports[0]
    stats['total_breaches'] = latest.get('total_breaches', 0)
    stats['total_password_exposures'] = latest.get('password_exposures', 0)
    stats['total_stealer_logs'] = latest.get('stealer_logs', 0)
    stats['total_critical_sites'] = latest.get('critical_sites', 0)

    for report in reports[:10]:  # Last 10 scans
        severity = report.get('severity', 'error')
        stats['severity_breakdown'][severity] += 1

        stats['recent_scans'].append({
            'filename': report['filename'],
            'timestamp': report['timestamp'],
            'breaches': report.get('total_breaches', 0),
            'severity': severity
        })

    return jsonify(stats)

@app.route('/download/<filename>')
def download_report(filename):
    """Download a report file"""
    filepath = safe_path_join(REPORTS_DIR, filename)
    if filepath is None:
        abort(400, description="Invalid filename")
    if filepath.exists():
        return send_file(filepath, as_attachment=True)
    abort(404, description="File not found")


# Bitwarden HIBP Password Checker API Endpoints

@app.route('/api/bitwarden/status')
def api_bitwarden_status():
    """Check if Bitwarden integration is ready."""
    prereqs = bitwarden_checker.check_prerequisites()
    latest_report = bitwarden_checker.get_latest_report()

    return jsonify({
        'prerequisites': prereqs,
        'ready': all([
            prereqs['bw_installed'],
            prereqs['bw_session_set'],
            prereqs['vault_unlocked']
        ]),
        'latest_report': {
            'generated': latest_report.get('generated'),
            'summary': latest_report.get('summary')
        } if latest_report else None
    })


@app.route('/api/bitwarden/check', methods=['POST'])
def api_bitwarden_check():
    """Start a new Bitwarden password check."""
    prereqs = bitwarden_checker.check_prerequisites()

    if not prereqs['bw_session_set']:
        return jsonify({'error': 'BW_SESSION environment variable not set'}), 400
    if not prereqs['bw_installed']:
        return jsonify({'error': 'Bitwarden CLI not installed'}), 400
    if not prereqs['vault_unlocked']:
        return jsonify({'error': 'Bitwarden vault is locked'}), 400

    task_id = bitwarden_checker.start_check()
    return jsonify({'task_id': task_id, 'status': 'started'})


@app.route('/api/bitwarden/task/<task_id>')
def api_bitwarden_task_status(task_id):
    """Get status of a running password check."""
    status = bitwarden_checker.get_task_status(task_id)
    if status:
        return jsonify(status)
    return jsonify({'error': 'Task not found'}), 404


@app.route('/api/bitwarden/reports')
def api_bitwarden_reports():
    """Get list of all Bitwarden HIBP reports."""
    reports = bitwarden_checker.get_all_reports()
    return jsonify({'reports': reports})


@app.route('/api/bitwarden/report/<filename>')
def api_bitwarden_report_detail(filename):
    """Get detailed Bitwarden HIBP report."""
    report = bitwarden_checker.get_report_by_filename(filename)
    if report:
        return jsonify(report)
    return jsonify({'error': 'Report not found'}), 404


if __name__ == '__main__':
    # Run on localhost only for security
    app.run(host='127.0.0.1', port=5000, debug=False)
