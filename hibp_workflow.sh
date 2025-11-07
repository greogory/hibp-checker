#!/bin/bash

# HIBP Automated Workflow for Claude Code
# Wrapper script for comprehensive breach checking
# Author: Bosco's Automation Suite

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/hibp_comprehensive_checker.py"
CONFIG_FILE="${SCRIPT_DIR}/hibp_config.conf"
LOG_DIR="${SCRIPT_DIR}/logs"
REPORT_DIR="${SCRIPT_DIR}/reports"

# Create directories if they don't exist
mkdir -p "$LOG_DIR" "$REPORT_DIR"

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "${LOG_DIR}/hibp_workflow.log"
    
    case "$level" in
        ERROR)
            echo -e "${RED}[ERROR]${NC} $message" >&2
            ;;
        WARNING)
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        SUCCESS)
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        INFO)
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        *)
            echo "$message"
            ;;
    esac
}

# Load configuration
load_config() {
    # Preserve environment variable if already set (recommended method)
    local env_api_key="$HIBP_API_KEY"

    if [[ -f "$CONFIG_FILE" ]]; then
        source "$CONFIG_FILE"
        log INFO "Configuration loaded from $CONFIG_FILE"

        # If environment variable was set, use it (takes precedence)
        if [[ -n "$env_api_key" ]]; then
            HIBP_API_KEY="$env_api_key"
            log INFO "Using HIBP_API_KEY from environment variable"
        fi
    else
        log ERROR "Configuration file not found: $CONFIG_FILE"
        log INFO "Creating default configuration file..."
        create_default_config
        log WARNING "Please edit $CONFIG_FILE with your API key and settings"
        exit 1
    fi
}

# Create default configuration
create_default_config() {
    cat > "$CONFIG_FILE" << 'EOF'
# HIBP Configuration File
# ========================

# Your HIBP API Key (required)
# Get yours at: https://haveibeenpwned.com/API/Key
HIBP_API_KEY=""

# Email Configuration (use one or both options)
# -----------------------------------------------
# Option 1: Space-separated list
EMAIL_ADDRESSES=""
# Example: EMAIL_ADDRESSES="user1@domain.com user2@domain.com admin@company.com"

# Option 2: File containing emails (recommended for many addresses)
EMAIL_FILE=""
# Example: EMAIL_FILE="/home/bosco/my_emails.txt"
# Format: One email per line in the file

# Password Checking (optional - will be hashed before sending)
# -------------------------------------------------------------
PASSWORDS=""
PASSWORD_FILE=""

# Output Configuration
# --------------------
OUTPUT_FORMAT="text"  # Options: json, csv, text
VERBOSE=false         # Set to true for detailed output

# Notification Settings
# ---------------------
SEND_NOTIFICATIONS=false
NOTIFICATION_EMAIL=""
SLACK_WEBHOOK=""

# Only notify on new breaches since last check
NOTIFY_ONLY_NEW=true

# Automation Settings
# -------------------
ENABLE_SCHEDULED_CHECKS=false

# Cron schedule examples:
# "0 3 * * *"    - Daily at 3 AM
# "0 9 * * 1"    - Weekly on Monday at 9 AM  
# "0 0 1 * *"    - Monthly on the 1st at midnight
# "0 */6 * * *"  - Every 6 hours
SCHEDULE="0 3 * * *"

# Report Management
# -----------------
KEEP_REPORTS=30  # Keep last N reports (0 = keep all)
REPORT_DIR="${SCRIPT_DIR}/reports"
LOG_DIR="${SCRIPT_DIR}/logs"

# Security Triggers
# -----------------
TRIGGER_ON_PASSWORD_EXPOSURE=true
TRIGGER_ON_CRITICAL_SITES=true
TRIGGER_ON_NEW_BREACHES=true

# Rate Limiting (for Pwned 1 subscription)
# -----------------------------------------
# Pwned 1: 10 requests/minute
# Pwned 2: 50 requests/minute
# Pwned 3: 100 requests/minute
# Pwned 4: 500 requests/minute
RATE_LIMIT_DELAY=1.5  # Seconds between API calls

# Previous breach tracking (for new breach detection)
LAST_BREACH_FILE="${SCRIPT_DIR}/.last_breach_check"

EOF
}

# Validate configuration
validate_config() {
    # Check environment variable first (recommended), then config file
    if [[ -z "$HIBP_API_KEY" ]]; then
        log ERROR "HIBP_API_KEY is not set"
        log ERROR "Set it via environment variable: export HIBP_API_KEY=\"your-key\""
        log ERROR "Or set it in hibp_config.conf"
        exit 1
    fi
    
    if [[ -z "$EMAIL_ADDRESSES" ]] && [[ -z "$EMAIL_FILE" ]]; then
        log ERROR "No email addresses specified (EMAIL_ADDRESSES or EMAIL_FILE)"
        exit 1
    fi
    
    # Validate email file exists if specified
    if [[ -n "$EMAIL_FILE" ]] && [[ ! -f "$EMAIL_FILE" ]]; then
        log ERROR "Email file not found: $EMAIL_FILE"
        exit 1
    fi
    
    # Count total emails to check
    local email_count=0
    if [[ -n "$EMAIL_ADDRESSES" ]]; then
        email_count=$(echo "$EMAIL_ADDRESSES" | wc -w)
    fi
    if [[ -n "$EMAIL_FILE" ]]; then
        local file_count=$(grep -c '@' "$EMAIL_FILE" 2>/dev/null || echo 0)
        email_count=$((email_count + file_count))
    fi
    
    log INFO "Configured to check $email_count email address(es)"
    
    # Estimate time based on rate limit
    local estimated_time=$((email_count * 3 * 2))  # 3 API calls per email, 2 seconds each
    log INFO "Estimated completion time: ~${estimated_time} seconds"
}

# Create or update email file
manage_email_file() {
    local action="${1:-list}"
    local email_file="${EMAIL_FILE:-${SCRIPT_DIR}/my_emails.txt}"
    
    case "$action" in
        create)
            log INFO "Creating email list file: $email_file"
            cat > "$email_file" << 'EOF'
# HIBP Email List
# Add one email address per line
# Lines starting with # are ignored

EOF
            log SUCCESS "Email file created: $email_file"
            log INFO "Edit this file and add your email addresses (one per line)"
            ;;
        add)
            local new_email="${2:-}"
            if [[ -z "$new_email" ]]; then
                read -rp "Enter email address to add: " new_email
            fi
            if [[ "$new_email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
                echo "$new_email" >> "$email_file"
                log SUCCESS "Added $new_email to email list"
            else
                log ERROR "Invalid email format: $new_email"
            fi
            ;;
        list)
            if [[ -f "$email_file" ]]; then
                log INFO "Current email list ($email_file):"
                grep -v '^#' "$email_file" | grep '@' | nl
            else
                log WARNING "No email file found at: $email_file"
            fi
            ;;
        validate)
            if [[ -f "$email_file" ]]; then
                local valid_count=$(grep -E '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' "$email_file" | wc -l)
                local total_count=$(grep -v '^#' "$email_file" | grep '@' | wc -l)
                log INFO "Email validation: $valid_count/$total_count valid emails"
                if [[ "$valid_count" -ne "$total_count" ]]; then
                    log WARNING "Some emails may be malformed. Showing invalid lines:"
                    grep -v '^#' "$email_file" | grep '@' | grep -vE '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                fi
            fi
            ;;
    esac
}

# Track new breaches since last check
track_new_breaches() {
    local current_results="$1"
    local last_breach_file="${LAST_BREACH_FILE:-${SCRIPT_DIR}/.last_breach_check}"
    local new_breaches=""
    
    if [[ -f "$last_breach_file" ]]; then
        # Compare with previous results
        local old_breaches=$(cat "$last_breach_file")
        new_breaches=$(comm -13 <(echo "$old_breaches" | sort) <(echo "$current_results" | sort))
        
        if [[ -n "$new_breaches" ]]; then
            log WARNING "NEW BREACHES DETECTED since last check!"
            echo "$new_breaches"
            return 1
        else
            log INFO "No new breaches since last check"
            return 0
        fi
    else
        log INFO "First run - storing baseline for future breach detection"
    fi
    
    # Store current results for next comparison
    echo "$current_results" > "$last_breach_file"
}

# Run the Python checker
run_checker() {
    local cmd="python3 $PYTHON_SCRIPT -k '$HIBP_API_KEY'"
    
    # Add emails
    if [[ -n "$EMAIL_ADDRESSES" ]]; then
        cmd="$cmd -e $EMAIL_ADDRESSES"
    fi
    
    if [[ -n "$EMAIL_FILE" ]]; then
        cmd="$cmd --email-file '$EMAIL_FILE'"
    fi
    
    # Add passwords (optional)
    if [[ -n "$PASSWORDS" ]]; then
        cmd="$cmd -p $PASSWORDS"
    fi
    
    if [[ -n "$PASSWORD_FILE" ]]; then
        cmd="$cmd --password-file '$PASSWORD_FILE'"
    fi
    
    # Add output format
    cmd="$cmd -o $OUTPUT_FORMAT"
    
    # Add verbose flag
    if [[ "$VERBOSE" == "true" ]]; then
        cmd="$cmd -v"
    fi
    
    log INFO "Starting HIBP comprehensive check..."
    
    # Run the command and capture output
    local output
    local exit_code
    
    if output=$(eval "$cmd" 2>&1); then
        exit_code=$?
    else
        exit_code=$?
    fi
    
    # Move report to reports directory
    local report_file=$(echo "$output" | grep -oP 'report saved to: \K.*' || true)
    if [[ -n "$report_file" ]] && [[ -f "$report_file" ]]; then
        mv "$report_file" "$REPORT_DIR/"
        report_file="${REPORT_DIR}/$(basename "$report_file")"
        log SUCCESS "Report saved to: $report_file"
    fi
    
    # Process exit code
    case $exit_code in
        0)
            log SUCCESS "No breaches detected - all clear!"
            ;;
        1)
            log WARNING "Breaches detected - review report for details"
            trigger_actions "breach" "$report_file"
            ;;
        2)
            log ERROR "CRITICAL: Password exposures or critical sites compromised!"
            trigger_actions "critical" "$report_file"
            ;;
        *)
            log ERROR "Check failed with exit code: $exit_code"
            ;;
    esac
    
    echo "$output"
    return $exit_code
}

# Trigger automated actions based on findings
trigger_actions() {
    local severity="$1"
    local report="$2"
    
    if [[ "$SEND_NOTIFICATIONS" == "true" ]]; then
        send_notification "$severity" "$report"
    fi
    
    if [[ "$severity" == "critical" ]]; then
        log WARNING "Triggering critical security actions..."
        
        # Add custom actions here for critical findings
        # Example: Force password reset, disable accounts, etc.
        
        if [[ "$TRIGGER_ON_CRITICAL_SITES" == "true" ]]; then
            log INFO "Critical sites compromised - initiating security protocol"
            # Add your custom security protocol here
        fi
    fi
}

# Send notifications
send_notification() {
    local severity="$1"
    local report="$2"
    
    # Slack notification
    if [[ -n "$SLACK_WEBHOOK" ]]; then
        send_slack_notification "$severity" "$report"
    fi
    
    # Email notification
    if [[ -n "$NOTIFICATION_EMAIL" ]]; then
        send_email_notification "$severity" "$report"
    fi
}

# Send Slack notification
send_slack_notification() {
    local severity="$1"
    local report="$2"
    
    local color
    local title
    
    case "$severity" in
        critical)
            color="danger"
            title="🚨 CRITICAL: HIBP Security Alert"
            ;;
        breach)
            color="warning"
            title="⚠️ HIBP Breach Detection"
            ;;
        *)
            color="good"
            title="✅ HIBP Check Complete"
            ;;
    esac
    
    local payload=$(cat <<EOF
{
    "attachments": [{
        "color": "$color",
        "title": "$title",
        "text": "Automated HIBP check completed. Report: $(basename "$report")",
        "fields": [
            {
                "title": "Severity",
                "value": "$severity",
                "short": true
            },
            {
                "title": "Timestamp",
                "value": "$(date '+%Y-%m-%d %H:%M:%S')",
                "short": true
            }
        ]
    }]
}
EOF
    )
    
    curl -X POST -H 'Content-type: application/json' \
         --data "$payload" "$SLACK_WEBHOOK" 2>/dev/null || \
         log ERROR "Failed to send Slack notification"
}

# Send email notification
send_email_notification() {
    local severity="$1"
    local report="$2"
    
    # Using mail command (requires configured MTA)
    if command -v mail >/dev/null 2>&1; then
        local subject="HIBP Alert - Severity: $severity"
        mail -s "$subject" -a "$report" "$NOTIFICATION_EMAIL" < "$report" || \
            log ERROR "Failed to send email notification"
    else
        log WARNING "Mail command not available - skipping email notification"
    fi
}

# Cleanup old reports
cleanup_reports() {
    if [[ "$KEEP_REPORTS" -gt 0 ]]; then
        log INFO "Cleaning up old reports (keeping last $KEEP_REPORTS)"
        
        # Find and delete old reports
        find "$REPORT_DIR" -type f -name "hibp_report_*" | \
            sort -r | \
            tail -n +$((KEEP_REPORTS + 1)) | \
            xargs -r rm -f
    fi
}

# Setup cron job for scheduled checks
setup_schedule() {
    if [[ "$ENABLE_SCHEDULED_CHECKS" != "true" ]]; then
        log INFO "Scheduled checks are disabled"
        return
    fi
    
    local cron_entry="$SCHEDULE $SCRIPT_DIR/$(basename "$0") --run-scheduled"
    
    # Check if cron entry exists
    if crontab -l 2>/dev/null | grep -q "$SCRIPT_DIR/$(basename "$0")"; then
        log INFO "Scheduled check already configured"
    else
        log INFO "Setting up scheduled check: $SCHEDULE"
        (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
        log SUCCESS "Scheduled check configured successfully"
    fi
}

# Interactive mode for first-time setup
interactive_setup() {
    echo -e "${BLUE}HIBP Comprehensive Checker - Interactive Setup${NC}"
    echo "============================================="
    
    # API Key
    read -rp "Enter your HIBP API key: " api_key
    sed -i "s/^HIBP_API_KEY=.*/HIBP_API_KEY=\"$api_key\"/" "$CONFIG_FILE"
    
    # Email configuration
    echo ""
    echo "Email Configuration Options:"
    echo "1) Enter email addresses directly (good for 1-5 emails)"
    echo "2) Use a file with email list (recommended for many emails)"
    echo "3) Both (some direct, some in file)"
    
    read -rp "Choose option (1/2/3): " email_option
    
    case "$email_option" in
        1)
            echo "Enter email addresses (space-separated):"
            read -rp "> " emails
            sed -i "s/^EMAIL_ADDRESSES=.*/EMAIL_ADDRESSES=\"$emails\"/" "$CONFIG_FILE"
            ;;
        2)
            echo "Would you like to:"
            echo "a) Create a new email file"
            echo "b) Use existing email file"
            read -rp "Choose (a/b): " file_choice
            
            if [[ "$file_choice" == "a" ]]; then
                local email_file="${SCRIPT_DIR}/my_emails.txt"
                echo "Creating email file: $email_file"
                cat > "$email_file" << 'EOF'
# HIBP Email List
# Add one email address per line
# Lines starting with # are ignored

EOF
                echo "Enter email addresses (one per line, empty line to finish):"
                while IFS= read -r email; do
                    [[ -z "$email" ]] && break
                    echo "$email" >> "$email_file"
                done
                sed -i "s|^EMAIL_FILE=.*|EMAIL_FILE=\"$email_file\"|" "$CONFIG_FILE"
                echo "Added $(grep -c '@' "$email_file") email addresses to file"
            else
                read -rp "Enter path to existing email file: " email_file
                sed -i "s|^EMAIL_FILE=.*|EMAIL_FILE=\"$email_file\"|" "$CONFIG_FILE"
            fi
            ;;
        3)
            echo "Enter direct email addresses (space-separated):"
            read -rp "> " emails
            sed -i "s/^EMAIL_ADDRESSES=.*/EMAIL_ADDRESSES=\"$emails\"/" "$CONFIG_FILE"
            
            read -rp "Enter path to email file: " email_file
            sed -i "s|^EMAIL_FILE=.*|EMAIL_FILE=\"$email_file\"|" "$CONFIG_FILE"
            ;;
    esac
    
    # Output format
    echo ""
    echo "Output format:"
    echo "1) Text (human-readable)"
    echo "2) JSON (for processing)"
    echo "3) CSV (for spreadsheets)"
    read -rp "Choose format (1/2/3) [default: 1]: " format_choice
    
    case "${format_choice:-1}" in
        1) sed -i "s/^OUTPUT_FORMAT=.*/OUTPUT_FORMAT=\"text\"/" "$CONFIG_FILE" ;;
        2) sed -i "s/^OUTPUT_FORMAT=.*/OUTPUT_FORMAT=\"json\"/" "$CONFIG_FILE" ;;
        3) sed -i "s/^OUTPUT_FORMAT=.*/OUTPUT_FORMAT=\"csv\"/" "$CONFIG_FILE" ;;
    esac
    
    # Verbose output
    read -rp "Enable verbose output? (y/n) [n]: " verbose
    if [[ "$verbose" == "y" ]]; then
        sed -i "s/^VERBOSE=.*/VERBOSE=true/" "$CONFIG_FILE"
    fi
    
    # Scheduled checks
    echo ""
    read -rp "Enable automated scheduled checks? (y/n) [y]: " scheduled
    if [[ "${scheduled:-y}" == "y" ]]; then
        sed -i "s/^ENABLE_SCHEDULED_CHECKS=.*/ENABLE_SCHEDULED_CHECKS=true/" "$CONFIG_FILE"
        
        echo "Schedule options:"
        echo "1) Daily at 3 AM"
        echo "2) Weekly on Monday at 9 AM"
        echo "3) Every 6 hours"
        echo "4) Custom cron expression"
        read -rp "Choose schedule (1/2/3/4) [1]: " schedule_choice
        
        case "${schedule_choice:-1}" in
            1) schedule="0 3 * * *" ;;
            2) schedule="0 9 * * 1" ;;
            3) schedule="0 */6 * * *" ;;
            4) 
                read -rp "Enter cron expression: " schedule
                ;;
        esac
        
        sed -i "s|^SCHEDULE=.*|SCHEDULE=\"$schedule\"|" "$CONFIG_FILE"
    fi
    
    # Notifications
    echo ""
    read -rp "Enable notifications for breaches? (y/n) [n]: " notify
    if [[ "$notify" == "y" ]]; then
        sed -i "s/^SEND_NOTIFICATIONS=.*/SEND_NOTIFICATIONS=true/" "$CONFIG_FILE"
        
        read -rp "Email address for notifications: " notify_email
        if [[ -n "$notify_email" ]]; then
            sed -i "s/^NOTIFICATION_EMAIL=.*/NOTIFICATION_EMAIL=\"$notify_email\"/" "$CONFIG_FILE"
        fi
        
        read -rp "Slack webhook URL (optional, press Enter to skip): " slack_url
        if [[ -n "$slack_url" ]]; then
            sed -i "s|^SLACK_WEBHOOK=.*|SLACK_WEBHOOK=\"$slack_url\"|" "$CONFIG_FILE"
        fi
        
        read -rp "Only notify on NEW breaches? (y/n) [y]: " new_only
        if [[ "${new_only:-y}" == "y" ]]; then
            sed -i "s/^NOTIFY_ONLY_NEW=.*/NOTIFY_ONLY_NEW=true/" "$CONFIG_FILE"
        fi
    fi
    
    log SUCCESS "Setup complete! Configuration saved to $CONFIG_FILE"
    
    echo ""
    read -rp "Would you like to run a check now? (y/n) [y]: " run_now
    if [[ "${run_now:-y}" == "y" ]]; then
        validate_config
        run_checker
    fi
}

# Main execution
main() {
    local action="${1:-check}"
    
    case "$action" in
        check)
            load_config
            validate_config
            run_checker
            cleanup_reports
            ;;
        setup)
            if [[ ! -f "$CONFIG_FILE" ]]; then
                create_default_config
            fi
            interactive_setup
            setup_schedule
            ;;
        schedule)
            load_config
            setup_schedule
            ;;
        emails)
            # Email management subcommands
            local subcmd="${2:-list}"
            load_config
            manage_email_file "$subcmd" "${3:-}"
            ;;
        add-email)
            load_config
            manage_email_file "add" "${2:-}"
            ;;
        list-emails)
            load_config
            manage_email_file "list"
            ;;
        validate-emails)
            load_config
            manage_email_file "validate"
            ;;
        --run-scheduled)
            load_config
            validate_config
            log INFO "Running scheduled HIBP check"
            run_checker
            cleanup_reports
            ;;
        test)
            log INFO "Testing configuration and API connection..."
            load_config
            validate_config
            VERBOSE=true
            EMAIL_ADDRESSES="test@example.com"
            run_checker || true
            ;;
        help|--help|-h)
            cat << EOF
HIBP Comprehensive Checker - Automated Workflow

Usage: $(basename "$0") [action] [options]

Actions:
    check           Run HIBP check with current configuration (default)
    setup           Interactive setup wizard
    schedule        Setup/update scheduled checks
    emails [cmd]    Manage email lists:
                    - create: Create new email file
                    - add [email]: Add email to list
                    - list: Show current emails
                    - validate: Check email format
    add-email       Quick add email to list
    list-emails     Show configured emails
    validate-emails Check email format validity
    test            Test configuration and API connection
    help            Show this help message

Configuration file: $CONFIG_FILE
Email file: ${EMAIL_FILE:-Not configured}
Reports directory: $REPORT_DIR
Logs directory: $LOG_DIR

Examples:
    # Initial setup
    $(basename "$0") setup
    
    # Create and manage email list
    $(basename "$0") emails create
    $(basename "$0") add-email bosco@example.com
    $(basename "$0") list-emails
    
    # Run check
    $(basename "$0") check
    
    # Setup daily checks
    $(basename "$0") schedule

For Claude Code integration:
    claude-code run $(basename "$0") check

EOF
            ;;
        *)
            log ERROR "Unknown action: $action"
            echo "Use '$(basename "$0") help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
