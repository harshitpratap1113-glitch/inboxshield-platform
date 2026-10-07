import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "InboxShield AI — 100% Primary Inbox Outbound Engine"
    VERSION: str = "1.0.0"
    DEFAULT_SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    DEFAULT_SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    DEFAULT_SMTP_USER: str = os.getenv("SMTP_USER", "harshitpratap1113@gmail.com")
    DEFAULT_SMTP_PASS: str = os.getenv("SMTP_PASS", "jyfzhfxqvchvdkrx")
    APP_URL: str = os.getenv("APP_URL", "https://inboxshield.vercel.app")

settings = Settings()
