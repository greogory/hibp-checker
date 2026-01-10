#!/usr/bin/env python3
"""
Bitwarden Password Checker for HIBP
Reads Bitwarden JSON export and checks all passwords against HIBP
"""

import argparse
import json
import hashlib
import requests
import sys
import time
from typing import Tuple, List, Dict
from pathlib import Path

# Security note: This tool intentionally displays account names and optionally
# usernames to help users identify which credentials need to be changed.
# Use --quiet mode to suppress account details in output.


def redact_sensitive(value: str, show_chars: int = 4) -> str:
    """Partially redact sensitive data for safer display.

    Shows first few characters to help identify the account while
    redacting the rest. This reduces log exposure while maintaining utility.

    Args:
        value: The sensitive string to redact
        show_chars: Number of characters to show (default 4)

    Returns:
        Partially redacted string like "exam***"
    """
    if not value:
        return "[empty]"
    if len(value) <= show_chars:
        return value[0] + "*" * (len(value) - 1)
    return value[:show_chars] + "*" * min(3, len(value) - show_chars)


def check_password(password: str) -> Tuple[bool, int]:
    """
    Check if a password has been pwned using HIBP API.
    Uses k-anonymity - only sends first 5 characters of SHA-1 hash.
    """
    if not password:
        return False, 0

    # Hash the password with SHA-1
    # SHA1 is required by HIBP API protocol, not used for security purposes
    sha1_hash = hashlib.sha1(password.encode('utf-8'), usedforsecurity=False).hexdigest().upper()
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]

    # Query HIBP API with k-anonymity
    url = f"https://api.pwnedpasswords.com/range/{prefix}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Search for our suffix in the results
        hashes = response.text.splitlines()
        for line in hashes:
            hash_suffix, count = line.split(':')
            if hash_suffix == suffix:
                return True, int(count)

        return False, 0

    except requests.RequestException as e:
        print(f"  Error: {e}", file=sys.stderr)
        return False, -1

def format_risk(count: int) -> str:
    """Format the breach count with color coding."""
    if count == 0:
        return "\033[0;32m✓ Safe\033[0m"
    elif count < 10:
        return f"\033[1;33m⚠ {count:,}x\033[0m"
    elif count < 100:
        return f"\033[0;31m✗ {count:,}x\033[0m"
    elif count < 1000:
        return f"\033[0;31m✗ {count:,}x HIGH\033[0m"
    else:
        return f"\033[1;31m✗✗ {count:,}x CRITICAL\033[0m"

def parse_bitwarden_json(file_path: str) -> List[Dict]:
    """Parse Bitwarden JSON export and extract login items."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Bitwarden exports have an 'items' array
        if 'items' in data:
            # Filter for login items that have passwords
            return [
                item for item in data['items']
                if item.get('type') == 1  # Type 1 = Login
                and item.get('login', {}).get('password')
            ]
        else:
            print("Error: Unexpected JSON format. Expected 'items' array.")
            return []

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file: {e}")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Check Bitwarden passwords against HIBP database"
    )
    parser.add_argument("file", nargs="?", help="Path to Bitwarden JSON export")
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress account details in output (security mode)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show usernames in output"
    )
    args = parser.parse_args()

    print("=" * 80)
    print("Bitwarden Password Checker for HIBP")
    print("=" * 80)
    print()

    # Get file path from command line or prompt
    if args.file:
        json_file = args.file
    else:
        json_file = input("Enter path to Bitwarden JSON export: ").strip()

    if not json_file:
        print("Error: No file specified")
        sys.exit(1)

    # Expand ~ to home directory
    json_file = str(Path(json_file).expanduser())

    print(f"Reading: {json_file}")
    print()

    # Parse Bitwarden export
    items = parse_bitwarden_json(json_file)

    if not items:
        print("No login items found in export.")
        sys.exit(1)

    print(f"Found {len(items)} login items with passwords")
    print()

    # Track statistics
    total = len(items)
    safe = 0
    compromised = 0
    errors = 0
    critical = []

    print("Checking passwords against HIBP...")
    print("-" * 80)

    # Check each password
    for i, item in enumerate(items, 1):
        name = item.get('name', 'Unnamed')
        username = item.get('login', {}).get('username', '')
        password = item.get('login', {}).get('password', '')

        # Display progress (respect quiet mode)
        if args.quiet:
            print(f"[{i}/{total}] Checking... ", end='', flush=True)
        else:
            print(f"[{i}/{total}] {name}", end='')
            if args.verbose and username:
                print(f" ({username})", end='')
            print("... ", end='', flush=True)

        # Check password
        is_pwned, count = check_password(password)

        if count == -1:
            print("ERROR")
            errors += 1
        elif is_pwned:
            print(format_risk(count))
            compromised += 1
            if count >= 1000:
                critical.append({
                    'name': name,
                    'username': username,
                    'count': count
                })
        else:
            print(format_risk(0))
            safe += 1

        # Rate limiting - be nice to HIBP API
        if i < total:
            time.sleep(0.1)  # 100ms delay between requests

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total passwords checked: {total}")
    print(f"\033[0;32m✓ Safe passwords:       {safe}\033[0m")
    print(f"\033[0;31m✗ Compromised passwords: {compromised}\033[0m")
    if errors > 0:
        print(f"  Errors:                {errors}")
    print()

    # Show critical items (respect quiet mode)
    if critical:
        print("\033[1;31m⚠ CRITICAL - Change these immediately:\033[0m")
        print("-" * 80)
        if args.quiet:
            print(f"  {len(critical)} critical account(s) need immediate password changes.")
            print("  Run without --quiet to see account details.")
        else:
            for item in sorted(critical, key=lambda x: x['count'], reverse=True):
                # Redact sensitive account info to reduce log exposure
                print(f"  • {redact_sensitive(item['name'], 6)}")
                if args.verbose and item['username']:
                    print(f"    Username: {redact_sensitive(item['username'], 4)}")
                print(f"    Found {item['count']:,} times in breaches")
        print()

    # Recommendations
    print("=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)
    if compromised > 0:
        print("  1. Change all compromised passwords immediately")
        print("  2. Use Bitwarden's password generator for new passwords")
        print("  3. Enable 2FA/MFA on all affected accounts")
        print("  4. Check for suspicious account activity")
    else:
        print("  ✓ All passwords are safe!")
    print()
    print("  • Delete the JSON export file after checking (contains plaintext passwords)")
    print("  • Use Bitwarden's Reports → Exposed Passwords for regular checks")
    print("=" * 80)
    print()

    # Offer to delete export file
    delete = input("Delete the JSON export file now? [y/N]: ").strip().lower()
    if delete == 'y':
        try:
            Path(json_file).unlink()
            print(f"✓ Deleted: {json_file}")
        except Exception as e:
            print(f"Error deleting file: {e}")
            print(f"Please manually delete: {json_file}")

if __name__ == "__main__":
    main()
