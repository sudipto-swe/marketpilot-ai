from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1.endpoints import (
    auth, products, reviews, competitors, agents, seo, marketing, approvals, insights
)

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="MarketPilot AI — AI-Powered E-commerce Multi-Agent Automation Platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(products.router, prefix=f"{settings.API_V1_STR}/products", tags=["Products"])
app.include_router(reviews.router, prefix=f"{settings.API_V1_STR}/reviews", tags=["Reviews & Analytics"])
app.include_router(competitors.router, prefix=f"{settings.API_V1_STR}/competitors", tags=["Competitor Intelligence"])
app.include_router(agents.router, prefix=f"{settings.API_V1_STR}/agents", tags=["Agent Control Center"])
app.include_router(seo.router, prefix=f"{settings.API_V1_STR}/seo", tags=["SEO Studio"])
app.include_router(marketing.router, prefix=f"{settings.API_V1_STR}/marketing", tags=["Marketing Workspace"])
app.include_router(approvals.router, prefix=f"{settings.API_V1_STR}/approvals", tags=["Human Approval Center"])
app.include_router(insights.router, prefix=f"{settings.API_V1_STR}/insights", tags=["Business Insights"])

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "llm_provider": settings.LLM_PROVIDER,
        "version": settings.VERSION
    }
