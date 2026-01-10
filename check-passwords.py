#!/usr/bin/env python3
"""
HIBP Pwned Passwords Checker
Securely checks passwords against the Have I Been Pwned database
Uses k-anonymity - only sends first 5 characters of SHA-1 hash

Security notes:
- Passwords are NEVER logged, stored, or transmitted in plaintext
- Only SHA-1 hashes are computed locally
- Only the first 5 characters of the hash are sent to HIBP (k-anonymity)
- Output shows only breach counts, never the passwords themselves
"""

import hashlib
import requests
import sys
import getpass
from typing import Tuple

def check_password(password: str) -> Tuple[bool, int]:
    """
    Check if a password has been pwned using HIBP API.

    Args:
        password: The password to check

    Returns:
        Tuple of (is_pwned, count) where:
        - is_pwned: True if password found in breaches
        - count: Number of times password appears in breaches
    """
    # Hash the password with SHA-1
    # SHA1 is required by HIBP API protocol, not used for security purposes
    sha1_hash = hashlib.sha1(password.encode('utf-8'), usedforsecurity=False).hexdigest().upper()

    # Split hash into prefix (first 5 chars) and suffix (rest)
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]

    # Query HIBP API with k-anonymity (only send first 5 chars)
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

        # Not found in breaches
        return False, 0

    except requests.RequestException as e:
        print(f"Error checking password: {e}", file=sys.stderr)
        return False, -1

def format_count(count: int) -> str:
    """Format the breach count with color coding."""
    if count == 0:
        return "\033[0;32m✓ Safe (not found in breaches)\033[0m"
    elif count < 10:
        return f"\033[1;33m⚠ Found {count:,} time{'s' if count != 1 else ''} (low risk)\033[0m"
    elif count < 100:
        return f"\033[0;31m✗ Found {count:,} times (medium risk)\033[0m"
    elif count < 1000:
        return f"\033[0;31m✗ Found {count:,} times (high risk)\033[0m"
    else:
        return f"\033[1;31m✗✗ Found {count:,} times (CRITICAL - change immediately!)\033[0m"

def main():
    """Main function - interactive password checker."""
    print("=" * 70)
    print("HIBP Pwned Passwords Checker")
    print("=" * 70)
    print()
    print("This tool checks if your passwords have been exposed in data breaches.")
    print()
    print("How it works:")
    print("  - Your password is hashed locally (SHA-1)")
    print("  - Only the first 5 characters of the hash are sent to HIBP")
    print("  - Your actual password NEVER leaves your computer")
    print("  - Uses k-anonymity to protect your privacy")
    print()
    print("=" * 70)
    print()

    # Check if running in batch mode (passwords from file/stdin)
    if len(sys.argv) > 1 and sys.argv[1] == '--batch':
        print("Batch mode: Reading passwords from stdin...")
        print()
        for line_num, password in enumerate(sys.stdin, 1):
            password = password.rstrip('\n\r')
            if not password:
                continue

            is_pwned, count = check_password(password)

            if count == -1:
                print(f"Password #{line_num}: Error checking")
            elif is_pwned:
                print(f"Password #{line_num}: {format_count(count)}")
            else:
                print(f"Password #{line_num}: {format_count(0)}")
    else:
        # Interactive mode
        print("Enter passwords to check (Ctrl+C or empty line to quit)")
        print()

        password_num = 1
        while True:
            try:
                # Get password securely (hidden input)
                password = getpass.getpass(f"Password #{password_num}: ")

                if not password:
                    print("\nDone!")
                    break

                # Check password
                is_pwned, count = check_password(password)

                if count == -1:
                    print("  └─ Error checking password\n")
                elif is_pwned:
                    print(f"  └─ {format_count(count)}\n")
                else:
                    print(f"  └─ {format_count(0)}\n")

                password_num += 1

            except KeyboardInterrupt:
                print("\n\nInterrupted. Exiting...")
                break
            except EOFError:
                print("\n\nDone!")
                break

    print()
    print("=" * 70)
    print("Recommendations:")
    print("  ✓ Use unique passwords for each service")
    print("  ✓ Use a password manager (Bitwarden, 1Password, etc.)")
    print("  ✓ Enable 2FA/MFA on all important accounts")
    print("  ✓ Change any passwords that show up in breaches")
    print("=" * 70)

if __name__ == "__main__":
    main()
