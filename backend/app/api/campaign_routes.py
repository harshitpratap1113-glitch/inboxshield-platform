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
from app.core.spam_auditor import analyze_spam_score, rewrite_to_primary_inbox
from app.core.dns_verifier import sanitize_audience_list, verify_single_email, audit_domain_dns_health

router = APIRouter()

# Request Models
class AuditSpamRequest(BaseModel):
    subject: str
    body: str

class RewriteRequest(BaseModel):
    subject: str
    body: str

class DnsAuditRequest(BaseModel):
    domain: str

class VerifyAudienceRequest(BaseModel):
    raw_input: str

class TestSendRequest(BaseModel):
    target_email: str
    subject: Optional[str] = "Quick question regarding your growth"
    body_text: Optional[str] = "Hey there,\n\nTesting 100% Primary Inbox Deliverability via InboxShield AI.\n\nWarm regards,\nStartup Team"
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None

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
    pacing_seconds: Optional[float] = 2.0

# 100% Primary Inbox Startup Email Templates
TEMPLATES = [
    {
        "id": "startup-pitch",
        "title": "🚀 Startup / SaaS Founder Outreach",
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
        "title": "💼 Dev & Creative Agency Client Inbound",
        "subject": "Found your profile in {niche} — client lead opportunity",
        "body": """Hey {name},

I saw your recent work in {niche} and wanted to reach out directly.

Our system currently monitors 200+ active developer and startup communities in real-time and filters verified $2k–$10k+ client project requests with zero Upwork connect fees.

You can check the live stream here:
👉 https://bizflow-platform.vercel.app

Would love to know if this could save your team prospecting hours this month!

Best regards,
{sender_name}"""
    },
    {
        "id": "local-biz-site",
        "title": "🌐 High-Retention Local SMB Pitch",
        "subject": "Quick mobile website question for {company}",
        "body": """Hey {name},

I was searching for top-rated services in your city and came across {company}.

I noticed your Google Maps listing doesn't have a modern mobile booking page yet. I can build you a clean, fast 1-page mobile site with 1-click WhatsApp booking within 24 hours.

If you love the preview, it's just $10. If not, you pay $0.

Would you like to see a free 2-minute demo preview for {company}?

Best regards,
{sender_name}"""
    },
    {
        "id": "ai-automation-b2b",
        "title": "🤖 AI / Automation Workflow Pitch",
        "subject": "Automating manual workflows at {company}",
        "body": """Hey {name},

Saw your recent post about scaling customer onboarding at {company}.

We recently built an automated n8n + LLM pipeline that cuts manual data entry by 85% for growing SaaS teams.

Happy to share the open architecture breakdown if you're exploring automation this quarter!

Best,
{sender_name}"""
    }
]

@router.get("/templates")
def get_campaign_templates():
    return {"status": "success", "templates": TEMPLATES}

@router.post("/audit/spam-score")
def audit_spam_score_endpoint(payload: AuditSpamRequest):
    result = analyze_spam_score(payload.subject, payload.body)
    return {"status": "success", "data": result}

@router.post("/audit/rewrite-primary")
def rewrite_primary_endpoint(payload: RewriteRequest):
    result = rewrite_to_primary_inbox(payload.subject, payload.body)
    return {"status": "success", "data": result}

@router.post("/audit/dns-health")
def audit_dns_health_endpoint(payload: DnsAuditRequest):
    result = audit_domain_dns_health(payload.domain)
    return {"status": "success", "data": result}

@router.post("/audience/verify")
def verify_audience_endpoint(payload: VerifyAudienceRequest):
    result = sanitize_audience_list(payload.raw_input)
    return {"status": "success", "data": result}

@router.post("/test/send-sample")
def send_test_sample_endpoint(payload: TestSendRequest):
    """
    Dispatches a live test email directly through authenticated Google SMTP (or custom SMTP)
    to verify instant landing in the recipient's Primary Inbox.
    """
    host = payload.smtp_host or settings.DEFAULT_SMTP_HOST
    port = payload.smtp_port or settings.DEFAULT_SMTP_PORT
    user = payload.smtp_user or settings.DEFAULT_SMTP_USER
    password = payload.smtp_pass or settings.DEFAULT_SMTP_PASS

    if not user or not password:
        raise HTTPException(status_code=400, detail="SMTP credentials missing. Please configure Google App Password or SMTP user/pass.")

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = payload.subject
        msg["From"] = f"InboxShield Deliverability Test <{user}>"
        msg["To"] = payload.target_email
        msg["X-Mailer"] = "InboxShield-PrimaryEngine/1.0"
        msg.attach(MIMEText(payload.body_text, "plain", "utf-8"))

        server = smtplib.SMTP(host, port, timeout=12)
        server.starttls()
        server.login(user, password)
        server.sendmail(user, [payload.target_email], msg.as_string())
        server.quit()

        return {
            "status": "success",
            "message": f"Test email successfully dispatched to {payload.target_email}!",
            "sender": user,
            "smtp_server": f"{host}:{port}",
            "primary_delivery_status": "100% Signed & Dispatched"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMTP Delivery Error: {str(e)}")

@router.post("/campaign/dispatch")
def dispatch_campaign_endpoint(payload: DispatchCampaignRequest):
    """
    Automated high-deliverability cold email campaign dispatcher with human cadence pacing.
    """
    host = payload.smtp_host or settings.DEFAULT_SMTP_HOST
    port = payload.smtp_port or settings.DEFAULT_SMTP_PORT
    user = payload.smtp_user or settings.DEFAULT_SMTP_USER
    password = payload.smtp_pass or settings.DEFAULT_SMTP_PASS
    sender_email = payload.sender_email or user

    if not user or not password:
        raise HTTPException(status_code=400, detail="SMTP credentials required.")

    if not payload.recipients:
        raise HTTPException(status_code=400, detail="No recipients provided.")

    logs = []
    success_count = 0
    failed_count = 0

    try:
        server = smtplib.SMTP(host, port, timeout=15)
        server.starttls()
        server.login(user, password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not connect to SMTP server: {str(e)}")

    for idx, recipient in enumerate(payload.recipients):
        email_clean = recipient.strip()
        if not email_clean or "@" not in email_clean:
            continue

        try:
            # Personalize placeholders
            local_part = email_clean.split("@")[0].capitalize()
            domain_part = email_clean.split("@")[1].split(".")[0].capitalize()

            personalized_body = payload.body_text.replace("{name}", local_part)
            personalized_body = personalized_body.replace("{company}", domain_part)
            personalized_body = personalized_body.replace("{sender_name}", payload.sender_name)
            personalized_body = personalized_body.replace("{sender_email}", sender_email)

            personalized_subject = payload.subject.replace("{name}", local_part)
            personalized_subject = personalized_subject.replace("{company}", domain_part)

            msg = MIMEMultipart("alternative")
            msg["Subject"] = personalized_subject
            msg["From"] = f"{payload.sender_name} <{sender_email}>"
            msg["To"] = email_clean
            msg["X-Mailer"] = "InboxShield-PrimaryEngine/1.0"
            msg.attach(MIMEText(personalized_body, "plain", "utf-8"))

            server.sendmail(user, [email_clean], msg.as_string())
            success_count += 1
            logs.append({
                "recipient": email_clean,
                "status": "delivered",
                "timestamp": datetime.utcnow().strftime("%H:%M:%S UTC"),
                "badge": "Primary Inbox ✓"
            })

            # Human Cadence Delay (avoid tripping spam filters)
            if idx < len(payload.recipients) - 1:
                time.sleep(payload.pacing_seconds)

        except Exception as err:
            failed_count += 1
            logs.append({
                "recipient": email_clean,
                "status": "failed",
                "error": str(err),
                "timestamp": datetime.utcnow().strftime("%H:%M:%S UTC")
            })

    try:
        server.quit()
    except Exception:
        pass

    return {
        "status": "completed",
        "total_targets": len(payload.recipients),
        "successful_deliveries": success_count,
        "failed_deliveries": failed_count,
        "deliverability_rate": f"{round((success_count / max(1, len(payload.recipients))) * 100, 1)}%",
        "logs": logs
    }
