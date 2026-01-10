#!/usr/bin/env python3
"""
Bitwarden HIBP Streaming Checker

Reads Bitwarden vault items directly from stdin (via `bw list items`)
and checks passwords against Have I Been Pwned without creating any files.

Usage:
    bw list items | python bw-hibp-stream.py
    bw list items | python bw-hibp-stream.py --report json > report.json
    bw list items | python bw-hibp-stream.py --report csv --output report.csv

Security: Passwords are processed in memory only - never written to disk.
"""

import argparse
import csv
import hashlib
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from typing import Optional


@dataclass
class CheckResult:
    """Result of checking a single credential."""
    name: str
    username: str
    uri: str
    is_pwned: bool
    breach_count: int
    error: Optional[str] = None

    @property
    def status(self) -> str:
        if self.error:
            return "error"
        return "compromised" if self.is_pwned else "safe"

    @property
    def risk_level(self) -> str:
        if self.error:
            return "unknown"
        if not self.is_pwned:
            return "safe"
        if self.breach_count >= 1000:
            return "critical"
        if self.breach_count >= 100:
            return "high"
        if self.breach_count >= 10:
            return "medium"
        return "low"


def check_password_hibp(password: str) -> tuple[bool, int, Optional[str]]:
    """
    Check password against HIBP using k-anonymity.
    Only the first 5 characters of the SHA-1 hash are sent to the API.

    Returns: (is_pwned, breach_count, error_message)
    """
    if not password:
        return False, 0, None

    try:
        import requests
    except ImportError:
        return False, -1, "requests library not installed"

    # SHA1 is required by HIBP API protocol, not used for security purposes
    sha1_hash = hashlib.sha1(password.encode('utf-8'), usedforsecurity=False).hexdigest().upper()
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]

    try:
        response = requests.get(
            f"https://api.pwnedpasswords.com/range/{prefix}",
            timeout=10,
            headers={"User-Agent": "bw-hibp-stream/1.0"}
        )
        response.raise_for_status()

        for line in response.text.splitlines():
            hash_suffix, count = line.split(':')
            if hash_suffix == suffix:
                return True, int(count), None

        return False, 0, None

    except Exception as e:
        return False, -1, str(e)


def format_risk_terminal(result: CheckResult) -> str:
    """Format result with terminal colors."""
    if result.error:
        return f"\033[1;33m? ERROR: {result.error}\033[0m"
    if not result.is_pwned:
        return "\033[0;32m✓ Safe\033[0m"

    count = result.breach_count
    if count >= 1000:
        return f"\033[1;31m✗✗ {count:,}x CRITICAL\033[0m"
    if count >= 100:
        return f"\033[0;31m✗ {count:,}x HIGH\033[0m"
    if count >= 10:
        return f"\033[1;33m⚠ {count:,}x MEDIUM\033[0m"
    return f"\033[0;33m⚠ {count:,}x LOW\033[0m"


def parse_vault_items(json_data: str) -> list[dict]:
    """Parse Bitwarden vault items from JSON."""
    try:
        items = json.loads(json_data)

        # Handle both direct array and {items: [...]} format
        if isinstance(items, dict) and 'items' in items:
            items = items['items']

        if not isinstance(items, list):
            print("Error: Expected JSON array of items", file=sys.stderr)
            return []

        # Filter for login items with passwords
        return [
            item for item in items
            if item.get('type') == 1  # Login type
            and item.get('login', {}).get('password')
        ]

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        return []


def check_all_passwords(items: list[dict], quiet: bool = False) -> list[CheckResult]:
    """Check all passwords and return results."""
    results = []
    total = len(items)

    for i, item in enumerate(items, 1):
        name = item.get('name', 'Unnamed')
        login = item.get('login', {})
        username = login.get('username', '')
        password = login.get('password', '')
        uris = login.get('uris', [])
        uri = uris[0].get('uri', '') if uris else ''

        if not quiet:
            print(f"[{i}/{total}] {name}", end='', file=sys.stderr)
            if username:
                print(f" ({username})", end='', file=sys.stderr)
            print("... ", end='', file=sys.stderr, flush=True)

        is_pwned, count, error = check_password_hibp(password)

        result = CheckResult(
            name=name,
            username=username,
            uri=uri,
            is_pwned=is_pwned,
            breach_count=count,
            error=error
        )
        results.append(result)

        if not quiet:
            print(format_risk_terminal(result), file=sys.stderr)

        # Rate limiting
        if i < total:
            time.sleep(0.1)

    return results


def generate_report_text(results: list[CheckResult]) -> str:
    """Generate plain text report."""
    lines = []
    lines.append("=" * 80)
    lines.append("BITWARDEN HIBP PASSWORD AUDIT REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    lines.append("")

    # Statistics
    total = len(results)
    safe = sum(1 for r in results if r.status == "safe")
    compromised = sum(1 for r in results if r.status == "compromised")
    errors = sum(1 for r in results if r.status == "error")
    critical = [r for r in results if r.risk_level == "critical"]
    high = [r for r in results if r.risk_level == "high"]

    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append(f"Total passwords checked: {total}")
    lines.append(f"Safe passwords:          {safe}")
    lines.append(f"Compromised passwords:   {compromised}")
    if errors:
        lines.append(f"Errors:                  {errors}")
    lines.append("")

    # Critical items
    if critical:
        lines.append("⚠ CRITICAL - Change immediately:")
        lines.append("-" * 40)
        for r in sorted(critical, key=lambda x: x.breach_count, reverse=True):
            lines.append(f"  • {r.name}")
            if r.username:
                lines.append(f"    Username: {r.username}")
            if r.uri:
                lines.append(f"    URI: {r.uri}")
            lines.append(f"    Found {r.breach_count:,} times in breaches")
        lines.append("")

    # High risk items
    if high:
        lines.append("⚠ HIGH RISK - Should change soon:")
        lines.append("-" * 40)
        for r in sorted(high, key=lambda x: x.breach_count, reverse=True):
            lines.append(f"  • {r.name} ({r.breach_count:,}x)")
            if r.username:
                lines.append(f"    Username: {r.username}")
        lines.append("")

    # All compromised (if not too many)
    compromised_results = [r for r in results if r.is_pwned]
    if compromised_results and len(compromised_results) <= 50:
        lines.append("ALL COMPROMISED PASSWORDS:")
        lines.append("-" * 40)
        for r in sorted(compromised_results, key=lambda x: x.breach_count, reverse=True):
            risk = r.risk_level.upper()
            lines.append(f"  [{risk:8}] {r.name}: {r.breach_count:,}x")
        lines.append("")

    lines.append("=" * 80)
    lines.append("RECOMMENDATIONS:")
    lines.append("=" * 80)
    if compromised:
        lines.append("  1. Change all compromised passwords immediately")
        lines.append("  2. Use Bitwarden's password generator (20+ chars)")
        lines.append("  3. Enable 2FA/MFA on all affected accounts")
        lines.append("  4. Check for suspicious account activity")
    else:
        lines.append("  ✓ All passwords are safe!")
    lines.append("")

    return "\n".join(lines)


def generate_report_json(results: list[CheckResult]) -> str:
    """Generate JSON report."""
    report = {
        "generated": datetime.now().isoformat(),
        "summary": {
            "total": len(results),
            "safe": sum(1 for r in results if r.status == "safe"),
            "compromised": sum(1 for r in results if r.status == "compromised"),
            "errors": sum(1 for r in results if r.status == "error"),
            "critical_count": sum(1 for r in results if r.risk_level == "critical"),
            "high_count": sum(1 for r in results if r.risk_level == "high"),
        },
        "items": [
            {
                "name": r.name,
                "username": r.username,
                "uri": r.uri,
                "status": r.status,
                "risk_level": r.risk_level,
                "breach_count": r.breach_count,
                "error": r.error,
            }
            for r in results
        ]
    }
    return json.dumps(report, indent=2)


def generate_report_csv(results: list[CheckResult]) -> str:
    """Generate CSV report."""
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Username", "URI", "Status", "Risk Level", "Breach Count", "Error"])

    for r in results:
        writer.writerow([
            r.name,
            r.username,
            r.uri,
            r.status,
            r.risk_level,
            r.breach_count if r.breach_count >= 0 else "",
            r.error or ""
        ])

    return output.getvalue()


def print_terminal_summary(results: list[CheckResult]):
    """Print summary to terminal (stderr)."""
    total = len(results)
    safe = sum(1 for r in results if r.status == "safe")
    compromised = sum(1 for r in results if r.status == "compromised")
    errors = sum(1 for r in results if r.status == "error")
    critical = sum(1 for r in results if r.risk_level == "critical")

    print("", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("SUMMARY", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Total:       {total}", file=sys.stderr)
    print(f"\033[0;32mSafe:        {safe}\033[0m", file=sys.stderr)
    print(f"\033[0;31mCompromised: {compromised}\033[0m", file=sys.stderr)
    if critical:
        print(f"\033[1;31mCritical:    {critical}\033[0m", file=sys.stderr)
    if errors:
        print(f"\033[1;33mErrors:      {errors}\033[0m", file=sys.stderr)
    print("=" * 60, file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Check Bitwarden passwords against HIBP (streaming, no files)",
        epilog="Example: bw list items | python %(prog)s --report json > report.json"
    )
    parser.add_argument(
        "--report", "-r",
        choices=["text", "json", "csv"],
        default="text",
        help="Report format (default: text)"
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write report to file instead of stdout"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output"
    )
    parser.add_argument(
        "--compromised-only", "-c",
        action="store_true",
        help="Only include compromised items in report"
    )

    args = parser.parse_args()

    # Check if stdin has data
    if sys.stdin.isatty():
        print("Error: No input received. Pipe Bitwarden data via stdin.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Usage:", file=sys.stderr)
        print("  bw list items | python bw-hibp-stream.py", file=sys.stderr)
        print("  bw list items | python bw-hibp-stream.py --report json", file=sys.stderr)
        print("", file=sys.stderr)
        print("Make sure you're logged in:", file=sys.stderr)
        print("  bw login", file=sys.stderr)
        print("  bw unlock", file=sys.stderr)
        print("  export BW_SESSION='...'", file=sys.stderr)
        sys.exit(1)

    # Read all input
    if not args.quiet:
        print("Reading vault items from stdin...", file=sys.stderr)

    json_input = sys.stdin.read()
    items = parse_vault_items(json_input)

    if not items:
        print("No login items with passwords found.", file=sys.stderr)
        sys.exit(1)

    if not args.quiet:
        print(f"Found {len(items)} login items with passwords", file=sys.stderr)
        print("", file=sys.stderr)
        print("Checking against HIBP (k-anonymity - your passwords stay local)...", file=sys.stderr)
        print("-" * 60, file=sys.stderr)

    # Check all passwords
    results = check_all_passwords(items, quiet=args.quiet)

    # Filter if requested
    if args.compromised_only:
        results = [r for r in results if r.is_pwned]

    # Print terminal summary
    if not args.quiet:
        print_terminal_summary(results)

    # Generate report
    if args.report == "json":
        report = generate_report_json(results)
    elif args.report == "csv":
        report = generate_report_csv(results)
    else:
        report = generate_report_text(results)

    # Output report
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        if not args.quiet:
            print(f"\nReport saved to: {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
