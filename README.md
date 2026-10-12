<div align="center">

# 🛡️ InboxShield AI — Cold Email Deliverability Suite

### *Guarantee 100% Primary Inbox Delivery with Real-Time Spam Auditing & DNS Health Verification*

[![Live Demo](https://img.shields.io/badge/Live_Demo-inboxshield--platform.vercel.app-10B981?style=for-the-badge&logo=vercel&logoColor=white)](https://inboxshield-platform.vercel.app)
[![DNS Auditor](https://img.shields.io/badge/DNS-SPF_•_DKIM_•_DMARC_•_MX-blue?style=for-the-badge&logo=cloudflare&logoColor=white)](https://inboxshield-platform.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Author](https://img.shields.io/badge/Author-Harshit_Pratap-DA552F?style=for-the-badge&logo=github&logoColor=white)](https://github.com/harshitpratap1113-glitch)

<br/>

<img src="https://trafficpulse-platform.vercel.app/tracker.js" alt="" width="0" height="0" />

</div>

---

## 🌟 Overview

**InboxShield AI** is an advanced cold email deliverability platform engineered to ensure your outbound emails hit the **Primary Inbox** rather than the Spam or Promotions folder. It performs real-time linguistic spam detection, calculates spam-trigger likelihood against major email service provider (ESP) filters, and validates domain authentication protocols (SPF, DKIM, DMARC, and MX records).

---

## ✨ Key Features

- 🔬 **Real-Time Spam Trigger Detector**: Analyzes email copy against 500+ trigger words, aggressive capitalization, spam punctuation patterns, and high-risk URL shorteners.
- 🌐 **DNS & Domain Health Radar**: Instant verification of sending domain authentication:
  - **SPF (Sender Policy Framework)** record validation.
  - **DKIM (DomainKeys Identified Mail)** selector health check.
  - **DMARC policy** inspection (`p=none`, `quarantine`, `reject`).
  - **MX (Mail Exchange)** server reachability and fallback routing.
- 🎯 **Primary Inbox Score Engine**: Dynamic 0–100% score gauge reflecting real deliverability probability.
- 💡 **Instant Actionable Fixes**: Highlights exact phrases triggering spam filters and suggests professional, high-converting alternatives.
- 📱 **Sleek 2-View Architecture**: Seamlessly switch between the **Deliverability Studio** and the **Live Delivery Radar**.

---

## 🛠️ Architecture & Tech Stack

- **Frontend**: Clean Vanilla JavaScript (ES6+), Modern Semantic HTML5, TailwindCSS aesthetic.
- **Auditing Engine**: Client-side regex heuristic evaluator + Edge DNS lookup pipeline.
- **Hosting & Infrastructure**: Vercel Edge Serverless Platform.
- **Telemetry**: Real-time traffic analytics via [TrafficPulse AI](https://trafficpulse-platform.vercel.app).

---

## 🚀 Quick Start & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/harshitpratap1113-glitch/inboxshield-platform.git
cd inboxshield-platform
```

### 2. Run locally
```bash
# Using Python
python -m http.server 8080

# Or using Node.js
npx serve .
```

Navigate to `http://localhost:8080` in your web browser.

---

## 🌐 Live Deployment

InboxShield AI is live on Vercel at:  
👉 **[https://inboxshield-platform.vercel.app](https://inboxshield-platform.vercel.app)**

---

## 👨‍💻 Author

**Harshit Pratap**  
- GitHub: [@harshitpratap1113-glitch](https://github.com/harshitpratap1113-glitch)  
- Product Hunt: [@harshit_pratap](https://www.producthunt.com/@harshit_pratap)  
- Email: [harshitpratap1113@gmail.com](mailto:harshitpratap1113@gmail.com)
