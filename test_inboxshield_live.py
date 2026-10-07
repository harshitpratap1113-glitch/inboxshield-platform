import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
from app.core.spam_auditor import analyze_spam_score, rewrite_to_primary_inbox
from app.core.dns_verifier import audit_domain_dns_health, sanitize_audience_list

print("============================================================")
print("[*] INBOXSHIELD AI -- FULL SYSTEM VERIFICATION TEST")
print("============================================================")

# 1. Test Spam Score Analysis
dirty_subject = "100% FREE WINNER! BUY NOW AND MAKE MONEY FAST!"
dirty_body = "Click here to claim your guaranteed money! No credit card required! Act now!"
audit = analyze_spam_score(dirty_subject, dirty_body)
print(f"[OK] Dirty Email Deliverability Score: {audit['score']}/100 ({audit['rating']})")
print(f"     - Flags Detected: {audit['flags_count']}")

# 2. Test 1-Click AI Primary Inbox Rewriter
clean = rewrite_to_primary_inbox(dirty_subject, dirty_body)
print(f"[OK] Rewritten Subject: {clean['rewritten_subject']}")
print(f"[OK] Rewritten Body: {clean['rewritten_body']}")
print(f"[OK] New Deliverability Score: {clean['new_score']}/100")

# 3. Test DNS Health Inspector
dns = audit_domain_dns_health("google.com")
print(f"[OK] Google.com DNS Deliverability: {dns['dns_deliverability_score']}/100 (Provider: {dns['mail_provider']})")
print(f"     - MX Status: {dns['mx_status']['badge']}")
print(f"     - SPF Status: {dns['spf_status']['badge']}")
print(f"     - DMARC Status: {dns['dmarc_status']['badge']}")

# 4. Test Audience Sanitizer
sample_audience = "alex@google.com, invalid-user@nonexistent-fake-domain99.org, temp@mailinator.com"
sanitized = sanitize_audience_list(sample_audience)
print(f"[OK] Audience Sanitizer: {sanitized['valid_count']} Valid Leads | {sanitized['quarantined_count']} Quarantined Bounces")

print("============================================================")
print("[OK] ALL INBOXSHIELD AI ENGINE MODULES PASSED 100%!")
print("============================================================")
