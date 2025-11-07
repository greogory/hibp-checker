#!/usr/bin/env python3
"""
HIBP Comprehensive Breach & Credential Stuffing Checker

⚡ Powered by Have I Been Pwned (https://haveibeenpwned.com) by Troy Hunt
   Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
   https://creativecommons.org/licenses/by/4.0/

   This tool uses data from Have I Been Pwned. All breach and paste data
   is sourced from HIBP and must be attributed per CC BY 4.0 license.

Prerequisites:
   - Requires Have I Been Pwned API subscription (Pwned 1-4 tier)
   - Get API Key: https://haveibeenpwned.com/API/Key
   - API Documentation: https://haveibeenpwned.com/API/v3

Author: Bosco's Automation Workflow
Purpose: Deep dive into HIBP data to identify password compromises,
         stealer logs, and credential stuffing threats
"""

import requests
import json
import sys
import time
import argparse
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import csv

class HIBPChecker:
    """Comprehensive HIBP API checker for breach and credential stuffing data"""
    
    def __init__(self, api_key: str, verbose: bool = False):
        self.api_key = api_key
        self.verbose = verbose
        self.base_url = "https://haveibeenpwned.com/api/v3"
        self.pwned_pw_url = "https://api.pwnedpasswords.com/range"
        self.headers = {
            "hibp-api-key": api_key,
            "user-agent": "HIBP-Comprehensive-Checker-v1.0",
            "Accept": "application/json"
        }
        self.rate_limit_delay = 1.5  # seconds between requests
        self.results = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Logging with timestamp and level"""
        if self.verbose or level in ["ERROR", "WARNING", "CRITICAL"]:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")
    
    def make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling and rate limiting"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            self.log(f"Querying: {endpoint}")
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                self.log(f"No data found for {endpoint}", "INFO")
                return None
            elif response.status_code == 429:
                retry_after = response.headers.get('retry-after', '60')
                self.log(f"Rate limited. Retrying after {retry_after} seconds", "WARNING")
                time.sleep(int(retry_after))
                return self.make_request(endpoint, params)
            else:
                self.log(f"API error {response.status_code}: {response.text}", "ERROR")
                return None
                
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", "ERROR")
            return None
        finally:
            time.sleep(self.rate_limit_delay)
    
    def check_breaches(self, email: str) -> Dict:
        """Check all breaches for an email address"""
        self.log(f"Checking breaches for: {email}")
        
        # Get full breach details
        breaches = self.make_request(
            f"breachedaccount/{email}",
            params={"truncateResponse": "false"}
        )
        
        if not breaches:
            return {
                "email": email,
                "breaches": [],
                "breach_count": 0,
                "password_exposed": [],
                "stealer_logs": [],
                "verified_breaches": [],
                "unverified_breaches": [],
                "sensitive_breaches": [],
                "data_classes": set()
            }
        
        # Categorize breaches
        result = {
            "email": email,
            "breaches": breaches,
            "breach_count": len(breaches),
            "password_exposed": [],
            "stealer_logs": [],
            "verified_breaches": [],
            "unverified_breaches": [],
            "sensitive_breaches": [],
            "data_classes": set()
        }
        
        for breach in breaches:
            # Check if passwords were exposed
            if "Passwords" in breach.get("DataClasses", []):
                result["password_exposed"].append({
                    "name": breach["Name"],
                    "title": breach["Title"],
                    "date": breach["BreachDate"],
                    "password_type": self._analyze_password_exposure(breach)
                })
            
            # Check for stealer logs (credential stuffing data)
            if breach.get("IsStealerLog", False):
                result["stealer_logs"].append({
                    "name": breach["Name"],
                    "title": breach["Title"],
                    "date": breach["BreachDate"],
                    "pwn_count": breach["PwnCount"]
                })
            
            # Categorize by verification status
            if breach.get("IsVerified", False):
                result["verified_breaches"].append(breach["Name"])
            else:
                result["unverified_breaches"].append(breach["Name"])
            
            # Check for sensitive breaches
            if breach.get("IsSensitive", False):
                result["sensitive_breaches"].append(breach["Name"])
            
            # Collect all data classes
            for data_class in breach.get("DataClasses", []):
                result["data_classes"].add(data_class)
        
        result["data_classes"] = list(result["data_classes"])
        return result
    
    def _analyze_password_exposure(self, breach: Dict) -> str:
        """Analyze the type of password exposure in a breach"""
        description = breach.get("Description", "").lower()
        
        if "plain text" in description or "plaintext" in description:
            return "plaintext"
        elif "bcrypt" in description:
            return "bcrypt_hash"
        elif "sha-1" in description or "sha1" in description:
            return "sha1_hash"
        elif "sha-256" in description or "sha256" in description:
            return "sha256_hash"
        elif "md5" in description:
            return "md5_hash"
        elif "encrypted" in description:
            return "encrypted"
        elif "hashed" in description:
            return "hashed_unknown"
        else:
            return "unknown"
    
    def check_stealer_logs(self, email: str) -> Dict:
        """Check stealer logs for compromised credentials"""
        self.log(f"Checking stealer logs for: {email}")
        
        # Get domains where credentials were captured
        domains = self.make_request(f"stealerlogsbyemail/{email}")
        
        if not domains:
            return {"email": email, "compromised_sites": [], "count": 0}
        
        return {
            "email": email,
            "compromised_sites": domains,
            "count": len(domains),
            "critical": self._identify_critical_sites(domains)
        }
    
    def _identify_critical_sites(self, domains: List[str]) -> List[str]:
        """Identify critical sites in compromised list"""
        critical_patterns = [
            "bank", "paypal", "amazon", "google", "microsoft", "apple",
            "facebook", "twitter", "linkedin", "github", "gitlab",
            "aws", "azure", "digitalocean", "cloudflare", "namecheap",
            "godaddy", "stripe", "square", "venmo", "cashapp"
        ]
        
        critical = []
        for domain in domains:
            for pattern in critical_patterns:
                if pattern in domain.lower():
                    critical.append(domain)
                    break
        
        return critical
    
    def check_pastes(self, email: str) -> Dict:
        """Check if email appears in pastes"""
        self.log(f"Checking pastes for: {email}")
        
        pastes = self.make_request(f"pasteaccount/{email}")
        
        if not pastes:
            return {"email": email, "pastes": [], "count": 0}
        
        return {
            "email": email,
            "pastes": pastes,
            "count": len(pastes),
            "sources": list(set([p.get("Source", "Unknown") for p in pastes]))
        }
    
    def check_password(self, password: str) -> Dict:
        """Check if a password has been pwned"""
        self.log("Checking password against Pwned Passwords database")
        
        # Generate SHA-1 hash
        sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1[:5]
        suffix = sha1[5:]
        
        try:
            response = requests.get(
                f"{self.pwned_pw_url}/{prefix}",
                headers={"user-agent": self.headers["user-agent"]}
            )
            
            if response.status_code == 200:
                hashes = response.text.splitlines()
                for hash_line in hashes:
                    hash_suffix, count = hash_line.split(':')
                    if hash_suffix == suffix:
                        return {
                            "password_hash": sha1[:10] + "...",
                            "found": True,
                            "appearances": int(count),
                            "risk_level": self._assess_password_risk(int(count))
                        }
                
                return {
                    "password_hash": sha1[:10] + "...",
                    "found": False,
                    "appearances": 0,
                    "risk_level": "safe"
                }
            else:
                self.log(f"Password check failed: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"Password check error: {e}", "ERROR")
            return None
    
    def _assess_password_risk(self, count: int) -> str:
        """Assess password risk based on appearance count"""
        if count == 0:
            return "safe"
        elif count < 10:
            return "low"
        elif count < 100:
            return "medium"
        elif count < 1000:
            return "high"
        else:
            return "critical"
    
    def comprehensive_check(self, emails: List[str], passwords: List[str] = None) -> Dict:
        """Run comprehensive check on multiple emails and optional passwords"""
        results = {
            "scan_date": datetime.now().isoformat(),
            "emails_checked": [],
            "passwords_checked": [],
            "summary": {
                "total_breaches": 0,
                "password_exposures": 0,
                "stealer_log_hits": 0,
                "critical_sites_compromised": 0,
                "paste_exposures": 0
            }
        }
        
        # Check each email
        for email in emails:
            self.log(f"\n{'='*50}\nProcessing: {email}\n{'='*50}")
            
            email_result = {
                "email": email,
                "breaches": self.check_breaches(email),
                "stealer_logs": self.check_stealer_logs(email),
                "pastes": self.check_pastes(email)
            }
            
            # Update summary
            results["summary"]["total_breaches"] += email_result["breaches"]["breach_count"]
            results["summary"]["password_exposures"] += len(email_result["breaches"].get("password_exposed", []))
            results["summary"]["stealer_log_hits"] += email_result["stealer_logs"]["count"]
            results["summary"]["critical_sites_compromised"] += len(email_result["stealer_logs"].get("critical", []))
            results["summary"]["paste_exposures"] += email_result["pastes"]["count"]
            
            results["emails_checked"].append(email_result)
        
        # Check passwords if provided
        if passwords:
            self.log(f"\n{'='*50}\nChecking Passwords\n{'='*50}")
            for password in passwords:
                pw_result = self.check_password(password)
                if pw_result:
                    results["passwords_checked"].append(pw_result)
        
        return results
    
    def generate_report(self, results: Dict, output_format: str = "json") -> str:
        """Generate report in specified format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format == "json":
            filename = f"hibp_report_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        
        elif output_format == "csv":
            filename = f"hibp_report_{timestamp}.csv"
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Email", "Total Breaches", "Password Exposed", 
                    "Stealer Logs", "Critical Sites", "Pastes"
                ])
                
                for email_data in results["emails_checked"]:
                    email = email_data["email"]
                    breaches = email_data["breaches"]["breach_count"]
                    pw_exposed = len(email_data["breaches"]["password_exposed"])
                    stealer_logs = email_data["stealer_logs"]["count"]
                    critical = len(email_data["stealer_logs"].get("critical", []))
                    pastes = email_data["pastes"]["count"]
                    
                    writer.writerow([email, breaches, pw_exposed, stealer_logs, critical, pastes])
        
        elif output_format == "text":
            filename = f"hibp_report_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write("HIBP COMPREHENSIVE BREACH REPORT\n")
                f.write(f"Generated: {results['scan_date']}\n")
                f.write("="*60 + "\n\n")
                
                f.write("SUMMARY\n")
                f.write("-"*30 + "\n")
                for key, value in results["summary"].items():
                    f.write(f"{key.replace('_', ' ').title()}: {value}\n")
                f.write("\n")
                
                for email_data in results["emails_checked"]:
                    f.write(f"\nEMAIL: {email_data['email']}\n")
                    f.write("-"*30 + "\n")
                    
                    # Breaches
                    breaches = email_data["breaches"]
                    f.write(f"Total Breaches: {breaches['breach_count']}\n")
                    
                    if breaches["password_exposed"]:
                        f.write("\nPassword Exposed In:\n")
                        for pw in breaches["password_exposed"]:
                            f.write(f"  - {pw['title']} ({pw['date']}) - Type: {pw['password_type']}\n")
                    
                    # Stealer logs
                    stealer = email_data["stealer_logs"]
                    if stealer["count"] > 0:
                        f.write(f"\nCredentials Stolen For {stealer['count']} Sites:\n")
                        for site in stealer["compromised_sites"][:10]:  # First 10
                            f.write(f"  - {site}\n")
                        if stealer["count"] > 10:
                            f.write(f"  ... and {stealer['count'] - 10} more\n")
                        
                        if stealer.get("critical"):
                            f.write("\nCRITICAL SITES COMPROMISED:\n")
                            for site in stealer["critical"]:
                                f.write(f"  ⚠️  {site}\n")
                    
                    # Pastes
                    pastes = email_data["pastes"]
                    if pastes["count"] > 0:
                        f.write(f"\nFound in {pastes['count']} Pastes\n")
                        f.write(f"Sources: {', '.join(pastes['sources'])}\n")
                    
                    f.write("\n" + "="*60 + "\n")
        
        self.log(f"Report saved to: {filename}", "INFO")
        return filename

def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive HIBP breach and credential stuffing checker"
    )
    
    parser.add_argument(
        "-k", "--api-key",
        required=True,
        help="HIBP API key"
    )
    
    parser.add_argument(
        "-e", "--emails",
        nargs="+",
        help="Email addresses to check"
    )
    
    parser.add_argument(
        "-f", "--email-file",
        help="File containing email addresses (one per line)"
    )
    
    parser.add_argument(
        "-p", "--passwords",
        nargs="*",
        help="Passwords to check (optional)"
    )
    
    parser.add_argument(
        "--password-file",
        help="File containing passwords to check (one per line)"
    )
    
    parser.add_argument(
        "-o", "--output",
        choices=["json", "csv", "text"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Collect emails
    emails = []
    if args.emails:
        emails.extend(args.emails)
    
    if args.email_file:
        with open(args.email_file, 'r') as f:
            emails.extend([line.strip() for line in f if line.strip() and not line.strip().startswith('#')])
    
    if not emails:
        print("ERROR: No email addresses provided")
        sys.exit(1)
    
    # Collect passwords (optional)
    passwords = []
    if args.passwords:
        passwords.extend(args.passwords)
    
    if args.password_file:
        with open(args.password_file, 'r') as f:
            passwords.extend([line.strip() for line in f if line.strip()])
    
    # Initialize checker
    checker = HIBPChecker(args.api_key, verbose=args.verbose)
    
    # Run comprehensive check
    print(f"\nStarting comprehensive HIBP scan for {len(emails)} email(s)...")
    if passwords:
        print(f"Also checking {len(passwords)} password(s)...")
    
    results = checker.comprehensive_check(emails, passwords)
    
    # Generate report
    report_file = checker.generate_report(results, args.output)
    
    # Print summary to console
    print("\n" + "="*60)
    print("SCAN COMPLETE - SUMMARY")
    print("="*60)
    for key, value in results["summary"].items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print(f"\nDetailed report saved to: {report_file}")
    
    # Exit with appropriate code
    if results["summary"]["password_exposures"] > 0 or results["summary"]["critical_sites_compromised"] > 0:
        print("\n⚠️  CRITICAL: Password exposures or critical sites compromised detected!")
        print("ACTION REQUIRED: Change affected passwords immediately")
        sys.exit(2)
    elif results["summary"]["total_breaches"] > 0:
        print("\n⚠️  WARNING: Breaches detected. Review report for details.")
        sys.exit(1)
    else:
        print("\n✓ No breaches detected")
        sys.exit(0)

if __name__ == "__main__":
    main()
