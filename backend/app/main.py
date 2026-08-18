from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import analysis, reports, chat

app = FastAPI(
    title="OpenShift Operator Upgrade Advisor",
    description="AI-powered tool for analyzing OpenShift operator compatibility and upgrade paths",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
async def root():
    return {
        "message": "OpenShift Operator Upgrade Advisor API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
