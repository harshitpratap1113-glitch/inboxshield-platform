import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.api.campaign_routes import router as campaign_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(campaign_router, prefix="/api", tags=["InboxShield"])

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    candidates = [
        os.path.join(STATIC_DIR, "index.html"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "index.html"),
        os.path.join(os.getcwd(), "static", "index.html")
    ]
    for c in candidates:
        if os.path.exists(c):
            return FileResponse(c)
    return {"message": "InboxShield AI Backend is online!", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "healthy", "engine": "InboxShield 100% Primary Inbox Engine"}
