#!/bin/bash
# DNS TXT Record Verification Helper for HIBP
# Checks if the HIBP verification TXT records are properly configured

echo "HIBP Domain Verification Checker"
echo "================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_domain() {
    local domain=$1
    local expected_prefix=$2

    echo "Checking $domain..."
    echo ""

    # Try different DNS query methods
    if command -v dig &> /dev/null; then
        result=$(dig +short _hibp.$domain TXT 2>/dev/null)
    elif command -v host &> /dev/null; then
        result=$(host -t TXT _hibp.$domain 2>/dev/null | grep "hibp=" | cut -d'"' -f2)
    elif command -v nslookup &> /dev/null; then
        result=$(nslookup -type=TXT _hibp.$domain 2>/dev/null | grep "hibp=" | sed 's/.*"\(.*\)".*/\1/')
    else
        echo -e "${RED}✗ No DNS query tools available (dig, host, or nslookup)${NC}"
        echo "  Install bind-tools or dnsutils package"
        return 1
    fi

    if [ -z "$result" ]; then
        echo -e "${RED}✗ No TXT record found at _hibp.$domain${NC}"
        echo "  Expected: hibp=$expected_prefix..."
        echo "  Status: Record not yet added or not propagated"
        return 1
    else
        # Remove quotes if present
        result=$(echo "$result" | tr -d '"')

        if [[ "$result" == hibp=* ]]; then
            echo -e "${GREEN}✓ TXT record found!${NC}"
            echo "  Value: $result"

            if [[ "$result" == "hibp=$expected_prefix"* ]]; then
                echo -e "${GREEN}✓ Verification code matches!${NC}"
                echo ""
                echo "DNS verification successful for $domain"
                return 0
            else
                echo -e "${YELLOW}⚠ Warning: Code doesn't match expected value${NC}"
                echo "  Expected prefix: $expected_prefix"
                return 1
            fi
        else
            echo -e "${RED}✗ TXT record exists but wrong format${NC}"
            echo "  Found: $result"
            echo "  Expected format: hibp=..."
            return 1
        fi
    fi
}

# Check bsml.me
echo "Domain 1: bsml.me"
echo "Verification code: deml_4xdx8f4tnr92iikmtmuld5id"
echo "-------------------------------------------"
check_domain "bsml.me" "deml_4xdx8f4tnr92iikmtmuld5id"
bsml_status=$?

echo ""
echo ""

# Check thebosco.club
echo "Domain 2: thebosco.club"
echo "Verification code: deml_4s772pb4k8sln25fbmn4ht5s"
echo "-------------------------------------------"
check_domain "thebosco.club" "deml_4s772pb4k8sln25fbmn4ht5s"
bosco_status=$?

echo ""
echo ""
echo "Summary"
echo "======="
if [ $bsml_status -eq 0 ]; then
    echo -e "${GREEN}✓ bsml.me: Verified${NC}"
else
    echo -e "${RED}✗ bsml.me: Not verified${NC}"
fi

if [ $bosco_status -eq 0 ]; then
    echo -e "${GREEN}✓ thebosco.club: Verified${NC}"
else
    echo -e "${RED}✗ thebosco.club: Not verified${NC}"
fi
echo ""
echo "Next steps:"
echo "1. Add the TXT record to your DNS provider"
echo "2. Wait 5-15 minutes for propagation"
echo "3. Run this script again to verify"
echo "4. Once verified, go back to HIBP dashboard and complete verification"
