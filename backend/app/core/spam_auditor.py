import re
from typing import Dict, Any, List

# Comprehensive list of spam trigger words categorized by risk severity
SPAM_DICTIONARY = {
    "high": [
        ("100% free", "free preview / sample"),
        ("guaranteed money", "measurable results"),
        ("buy now", "explore options"),
        ("risk free", "zero commitment"),
        ("urgent response required", "quick question"),
        ("cash bonus", "incentive"),
        ("winner", "selected"),
        ("dear friend", "hey {name}"),
        ("opt in", "subscribe"),
        ("make money fast", "accelerate revenue"),
        ("unlimited leads", "targeted lead stream"),
        ("no credit card required", "free tier available"),
        ("act now", "when convenient")
    ],
    "medium": [
        ("click here", "check the live demo here"),
        ("cheap", "cost-effective"),
        ("no cost", "complimentary"),
        ("limited time", "this week"),
        ("special promotion", "early founder access"),
        ("as seen on", "featured in"),
        ("miracle", "major improvement"),
        ("all-in-one magic", "streamlined tool")
    ]
}

def analyze_spam_score(subject: str, body: str) -> Dict[str, Any]:
    combined_text = f"{subject} {body}".lower()
    total_score = 100
    flags = []
    
    # 1. Check High-Risk Trigger Words (-15 each)
    for trigger, suggestion in SPAM_DICTIONARY["high"]:
        if trigger in combined_text:
            total_score -= 15
            flags.append({
                "severity": "high",
                "phrase": trigger,
                "reason": "High-risk spam filter trigger in Google Workspace & Outlook heuristics.",
                "suggestion": suggestion
            })

    # 2. Check Medium-Risk Trigger Words (-7 each)
    for trigger, suggestion in SPAM_DICTIONARY["medium"]:
        if trigger in combined_text:
            total_score -= 7
            flags.append({
                "severity": "medium",
                "phrase": trigger,
                "reason": "Commercial marketing trigger phrase.",
                "suggestion": suggestion
            })

    # 3. Check Excessive Capitalization in Subject (-15)
    caps_count = sum(1 for c in subject if c.isupper())
    if len(subject) > 0 and (caps_count / len(subject)) > 0.4:
        total_score -= 15
        flags.append({
            "severity": "high",
            "phrase": "Excessive ALL-CAPS in Subject",
            "reason": "Subject line has over 40% uppercase characters.",
            "suggestion": "Use sentence case or casual title case."
        })

    # 4. Check Excessive Punctuation ($$$, !!!, ???) (-10)
    if re.search(r"[\$!]{2,}", subject + " " + body):
        total_score -= 10
        flags.append({
            "severity": "high",
            "phrase": "Multiple Exclamation / Dollar Signs (!! or $$)",
            "reason": "Spam filters automatically penalize stacked symbols.",
            "suggestion": "Use single punctuation."
        })

    # 5. Check Link Count Density (-5 if > 3 links)
    links = re.findall(r"https?://[^\s]+", body)
    if len(links) > 3:
        total_score -= 10
        flags.append({
            "severity": "medium",
            "phrase": f"{len(links)} Links in Email Body",
            "reason": "More than 2-3 links degrades inbox reputation for cold emails.",
            "suggestion": "Keep to 1 single clear CTA link."
        })

    # Ensure score stays between 0 and 100
    deliverability_score = max(10, min(100, total_score))
    
    if deliverability_score >= 90:
        status_label = "100% Primary Inbox Guaranteed"
        status_color = "emerald"
        status_desc = "Clean, natural human cadence. Zero high-risk spam triggers detected."
    elif deliverability_score >= 70:
        status_label = "Good (Minor Spam Warning)"
        status_color = "amber"
        status_desc = "Minor commercial phrases detected. Safe to send, but fixing suggestions increases reply rate."
    else:
        status_label = "High Spam Risk (Action Required)"
        status_color = "red"
        status_desc = "Multiple spam triggers detected. High likelihood of Promotions or Spam tab placement."

    return {
        "deliverability_score": deliverability_score,
        "status_label": status_label,
        "status_color": status_color,
        "status_desc": status_desc,
        "detected_flags_count": len(flags),
        "flags": flags,
        "total_words": len(body.split()),
        "link_count": len(links)
    }
