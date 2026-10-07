import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.spam_auditor import analyze_spam_score
from app.core.dns_verifier import sanitize_audience_list, verify_single_email
from app.api.campaign_routes import TEMPLATES

out = []
out.append("=================================================================")
out.append("🛡️ TESTING INBOXSHIELD AI PLATFORM BACKEND & AUDIT ENGINES")
out.append("=================================================================")

# 1. Test Spam Auditor
out.append("\n1. Testing AI Deliverability & Spam Score Heuristics...")
clean_subj = "Quick question regarding your growth at Acme"
clean_body = "Hey Alex, saw your work and would love to share a free demo preview."
audit_clean = analyze_spam_score(clean_subj, clean_body)
out.append(f"Clean Copy Score: {audit_clean['deliverability_score']}% ({audit_clean['status_label']})")
assert audit_clean['deliverability_score'] >= 90

spammy_subj = "BUY NOW 100% FREE $$$ WINNER"
spammy_body = "Click here for guaranteed money and cheap unlimited leads act now!"
audit_spam = analyze_spam_score(spammy_subj, spammy_body)
out.append(f"Spammy Copy Score: {audit_spam['deliverability_score']}% ({audit_spam['status_label']})")
out.append(f"Flagged Phrases: {[f['phrase'] for f in audit_spam['flags']]}")
assert audit_spam['deliverability_score'] < 60

# 2. Test DNS MX Sanitizer
out.append("\n2. Testing Pre-Send DNS & MX Sanitizer...")
raw_sample = "harshitpratap1113@gmail.com, alex@thoughtbot.com, fakeuser@nonexistentdomain1234999.com, invalid-email"
sanitized = sanitize_audience_list(raw_sample)
out.append(f"Total Extracted: {sanitized['total_extracted']}")
out.append(f"Valid DNS: {[l['email'] for l in sanitized['verified_leads']]}")
out.append(f"Quarantined (Bounce Prevented): {[q['email'] for q in sanitized['quarantined_leads']]}")
out.append(f"Audience Health: {sanitized['audience_health_score']}%")

assert len(sanitized['verified_leads']) >= 2
assert len(sanitized['quarantined_leads']) >= 1

# 3. Test Templates
out.append(f"\n3. Loaded Templates Count: {len(TEMPLATES)}")
for t in TEMPLATES:
    out.append(f"  - {t['title']}")

out.append("\n🎉 ALL INBOXSHIELD TESTS PASSED 100%!")

report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_suite_report.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("DONE")
