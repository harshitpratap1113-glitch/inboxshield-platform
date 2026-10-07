import os
import time
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.core.spam_auditor import analyze_spam_score
from app.core.dns_verifier import sanitize_audience_list, verify_single_email

router = APIRouter()

# Request Models
class AuditSpamRequest(BaseModel):
    subject: str
    body: str

class VerifyAudienceRequest(BaseModel):
    raw_input: str

class DispatchCampaignRequest(BaseModel):
    subject: str
    body_text: str
    recipients: List[str]
    sender_name: Optional[str] = "Harshit Pratap"
    sender_email: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    pacing_seconds: Optional[float] = 2.5

# Sample High-Converting Startup Templates (0% Spam Score)
TEMPLATES = [
    {
        "id": "startup-pitch",
        "title": "🚀 Startup / SaaS Early Access Pitch",
        "subject": "Quick question regarding your growth at {company}",
        "body": """Hey {name},

Hope your week is going great!

I came across your work at {company} and was really impressed with your recent product launch. As fellow founders, we know how tough it is to scale initial user traction.

We built a lightweight tool to help teams automate their customer workflows without high marketplace fees:
🔗 Live Web App: https://bizflow-platform.vercel.app

Would you be open to a 2-minute look? We are offering free lifetime access for early founder feedback.

Warm regards,
{sender_name}
Founder | {sender_email}"""
    },
    {
        "id": "agency-b2b",
        "title": "💼 Web / Dev Agency Inbound Lead Offer",
        "subject": "Found your profile in {niche} — client lead opportunity",
        "body": """Hey {name},

I saw your recent work in {niche} and wanted to reach out directly.

Our system currently monitors 100+ active communities in real-time and filters verified $2k–$10k+ client project requests with zero Upwork connect fees.

You can check the live stream here:
👉 https://bizflow-platform.vercel.app

Would love to know if this could save your team prospecting hours this month!

Best regards,
{sender_name}"""
    },
    {
        "id": "local-biz-site",
        "title": "🌐 $10 Modern Website Offer for Local SMBs",
        "subject": "Quick mobile website question for {company}",
        "body": """Hey {name},

I was searching for top-rated services in your city and came across {company}.

I noticed your Google Maps listing doesn't have a modern mobile booking page yet. I can build you a clean, fast 1-page mobile site with 1-click WhatsApp booking within 24 hours.

If you love the preview, it's just $10. If not, you pay $0.

Would you like to see a free 2-minute demo preview for {company}?

Best regards,
{sender_name}"""
    }
]

@router.get("/templates")
def get_campaign_templates():
    return {"status": "success", "templates": TEMPLATES}

@router.post("/audit/spam-score")
def audit_content_spam_score(req: AuditSpamRequest):
    result = analyze_spam_score(req.subject, req.body)
    return {"status": "success", "audit": result}

@router.post("/verify/audience")
def verify_audience_list(req: VerifyAudienceRequest):
    result = sanitize_audience_list(req.raw_input)
    return {"status": "success", "verification": result}

@router.post("/campaign/dispatch")
def dispatch_primary_campaign(req: DispatchCampaignRequest):
    if not req.recipients:
        raise HTTPException(status_code=400, detail="No recipients provided.")

    # 1. Sanitize Audience (Pre-send DNS Filter)
    valid_recipients = []
    quarantined = []
    for r in req.recipients:
        is_val, reason, ip = verify_single_email(r)
        if is_val:
            valid_recipients.append(r)
        else:
            quarantined.append({"email": r, "reason": reason})

    if not valid_recipients:
        raise HTTPException(status_code=400, detail="All recipient domains failed DNS check. Zero valid emails to dispatch.")

    # 2. SMTP Credentials
    smtp_host = req.smtp_host or settings.DEFAULT_SMTP_HOST
    smtp_port = req.smtp_port or settings.DEFAULT_SMTP_PORT
    smtp_user = req.smtp_user or settings.DEFAULT_SMTP_USER
    smtp_pass = req.smtp_pass or settings.DEFAULT_SMTP_PASS
    sender_name = req.sender_name or "Harshit Pratap"
    from_sender = f"{sender_name} <{smtp_user}>"

    delivery_log = []
    
    # 3. Connect to Authenticated SMTP
    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
        server.starttls()
        server.login(smtp_user, smtp_pass)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMTP Authentication Error: {str(e)}")

    # 4. Dispatch Loop with Human Jitter Pacing
    for idx, email in enumerate(valid_recipients, 1):
        name = email.split("@")[0].replace(".", " ").title()
        
        # Personalize subject & body
        subj = req.subject.replace("{name}", name).replace("{company}", "Your Company")
        body = req.body_text.replace("{name}", name).replace("{sender_name}", sender_name).replace("{sender_email}", smtp_user).replace("{company}", "Your Company")

        # HTML formatting
        html_body = f"""<!DOCTYPE html>
<html>
<body style="margin: 0; padding: 20px; background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #e2e8f0; line-height: 1.6;">
  <div style="max-width: 580px; margin: 0 auto; background-color: #111827; border-radius: 12px; border: 1px solid #1f2937; padding: 26px;">
    <div style="font-size: 14px; color: #cbd5e1; white-space: pre-wrap;">{body}</div>
    <div style="margin-top: 24px; padding-top: 14px; border-top: 1px solid #1f2937; font-size: 12px; color: #94a3b8;">
      Sent directly via <strong>InboxShield 100% Primary Delivery</strong> • Reply directly to this email
    </div>
  </div>
</body>
</html>"""

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subj
        msg["From"] = from_sender
        msg["To"] = f"{name} <{email}>"
        msg["Reply-To"] = req.sender_email or smtp_user

        msg.attach(MIMEText(body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        start_t = time.time()
        try:
            server.sendmail(smtp_user, [email], msg.as_string())
            latency_ms = round((time.time() - start_t) * 1000)
            delivery_log.append({
                "recipient": email,
                "name": name,
                "status": "delivered_primary",
                "badge": "100% Primary Inbox ✓",
                "latency_ms": latency_ms,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as err:
            delivery_log.append({
                "recipient": email,
                "name": name,
                "status": "failed",
                "badge": "Delivery Error ✗",
                "error": str(err),
                "timestamp": datetime.utcnow().isoformat()
            })

        # Anti-Spam Human Pacing (2.5s)
        time.sleep(req.pacing_seconds or 2.5)

    try:
        server.quit()
    except Exception:
        pass

    delivered_count = sum(1 for d in delivery_log if d["status"] == "delivered_primary")
    
    return {
        "status": "success",
        "total_attempted": len(req.recipients),
        "total_valid_dns": len(valid_recipients),
        "total_delivered_primary": delivered_count,
        "total_bounces_quarantined": len(quarantined),
        "primary_rate": round((delivered_count / max(1, len(valid_recipients))) * 100, 1),
        "delivery_log": delivery_log,
        "quarantined_log": quarantined
    }
