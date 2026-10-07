import re
import socket
from typing import Dict, Any, List, Tuple

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

def verify_single_email(email: str) -> Tuple[bool, str, str]:
    email = email.strip()
    if not re.match(EMAIL_REGEX, email):
        return False, "Invalid Email Format", ""

    domain = email.split("@")[1].strip().lower()
    try:
        ip = socket.gethostbyname(domain)
        return True, "Active DNS Host", ip
    except socket.gaierror:
        return False, f"Domain '{domain}' not found on internet (Fake / Non-existent)", ""
    except Exception as e:
        return False, f"DNS Verification Error: {str(e)}", ""

def sanitize_audience_list(raw_emails_or_text: str) -> Dict[str, Any]:
    # Extract all email addresses from text / CSV input
    extracted = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", raw_emails_or_text)
    
    # Remove duplicates preserving order
    seen = set()
    unique_emails = []
    for e in extracted:
        e_clean = e.strip().lower()
        if e_clean not in seen:
            seen.add(e_clean)
            unique_emails.append(e_clean)

    verified = []
    quarantined = []

    for email in unique_emails:
        is_valid, reason, ip = verify_single_email(email)
        if is_valid:
            verified.append({
                "email": email,
                "domain": email.split("@")[1],
                "status": "valid",
                "ip": ip,
                "badge": "DNS Verified ✓"
            })
        else:
            quarantined.append({
                "email": email,
                "domain": email.split("@")[1] if "@" in email else "unknown",
                "status": "quarantined",
                "reason": reason,
                "badge": "Bounce Blocked 🛡️"
            })

    total = len(unique_emails)
    health_score = round((len(verified) / max(1, total)) * 100, 1) if total > 0 else 100.0

    return {
        "total_extracted": total,
        "valid_count": len(verified),
        "quarantined_count": len(quarantined),
        "audience_health_score": health_score,
        "verified_leads": verified,
        "quarantined_leads": quarantined
    }
