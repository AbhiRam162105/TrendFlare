from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import get_settings
from routers import auth, content, publishing, analytics
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.dev.ConsoleRenderer(),
    ],
)

logger = structlog.get_logger()

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="TrendFlare.ai — AI-powered social media management API",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(publishing.router, prefix="/api/publishing", tags=["Publishing"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "TrendFlare API",
        "version": "1.0.0",
        "environment": settings.environment,
    }


@app.on_event("startup")
async def startup():
    logger.info("TrendFlare API starting", environment=settings.environment)


@app.on_event("shutdown")
async def shutdown():
    logger.info("TrendFlare API shutting down")
