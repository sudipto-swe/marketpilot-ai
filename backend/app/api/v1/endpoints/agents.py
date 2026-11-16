from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_workspace_id
from app.models.entities import AgentRun
from app.orchestration.coordinator import orchestrator

router = APIRouter()

AGENTS_METADATA = [
    {
        "id": "review_analysis",
        "name": "Review Analysis Agent",
        "role": "Customer Sentiment & Quality Analyst",
        "description": "Deterministic TF-IDF extraction, sentiment distribution, and grounded complaint categorization.",
        "icon": "MessageSquare"
    },
    {
        "id": "competitor_price_monitoring",
        "name": "Competitor Price Monitoring Agent",
        "role": "Pricing Intelligence Strategist",
        "description": "Compares real-time competitor prices, triggers alerts on undercut margins, and drafts approval requests.",
        "icon": "TrendingDown"
    },
    {
        "id": "seo_content_generation",
        "name": "SEO Content Generation Agent",
        "role": "Verified Product SEO Specialist",
        "description": "Generates keyword-optimized product copy, validated against verified attributes to prevent ungrounded claims.",
        "icon": "Search"
    },
    {
        "id": "marketing_campaign",
        "name": "Marketing Campaign Agent",
        "role": "Growth Marketing Director",
        "description": "Drafts omnichannel social and email campaigns with A/B variations for human editorial sign-off.",
        "icon": "Megaphone"
    },
    {
        "id": "business_insights",
        "name": "Business Insights Agent",
        "role": "Strategic Synthesis Lead",
        "description": "Integrates multi-agent intelligence, risk assessments, and executive recommendations requiring approval.",
        "icon": "Sparkles"
    }
]

@router.get("")
def get_agents_list(
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    res = []
    for meta in AGENTS_METADATA:
        agent_id = meta["id"]
        last_run = (
            db.query(AgentRun)
            .filter(AgentRun.workspace_id == workspace_id, AgentRun.agent_name == agent_id)
            .order_by(AgentRun.created_at.desc())
            .first()
        )
        total_runs = (
            db.query(AgentRun)
            .filter(AgentRun.workspace_id == workspace_id, AgentRun.agent_name == agent_id)
            .count()
        )
        res.append({
            **meta,
            "total_runs": total_runs,
            "last_run_time": last_run.created_at if last_run else None,
            "last_status": last_run.status if last_run else "idle",
            "last_summary": last_run.summary if last_run else "Ready to run"
        })
    return res

@router.post("/{agent_id}/run")
def run_individual_agent(
    agent_id: str,
    product_id: Optional[str] = None,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    # Resolve product_id if not supplied or if SKU was provided
    target_product_id = product_id
    if target_product_id:
        # Check if target_product_id is an ID or a SKU
        from app.models.entities import Product
        p = db.query(Product).filter(
            Product.workspace_id == workspace_id,
            (Product.id == target_product_id) | (Product.sku == target_product_id)
        ).first()
        if p:
            target_product_id = p.id
    elif agent_id in ["seo_content_generation", "review_analysis", "marketing_campaign"]:
        # Auto-fallback to first available product in workspace if none specified
        from app.models.entities import Product
        first_prod = db.query(Product).filter(Product.workspace_id == workspace_id).first()
        if first_prod:
            target_product_id = first_prod.id

    if agent_id == "review_analysis":
        return orchestrator.run_review_agent(db, workspace_id, target_product_id)
    elif agent_id == "competitor_price_monitoring":
        return orchestrator.run_price_agent(db, workspace_id)
    elif agent_id == "seo_content_generation":
        if not target_product_id:
            raise HTTPException(status_code=400, detail="A valid product_id or SKU is required for SEO Content Generation")
        return orchestrator.run_seo_agent(db, workspace_id, target_product_id)
    elif agent_id == "marketing_campaign":
        return orchestrator.run_marketing_agent(
            db, workspace_id,
            campaign_name="Targeted Seasonal Push",
            campaign_type="seasonal",
            product_id=target_product_id
        )
    elif agent_id == "business_insights":
        return orchestrator.run_insights_agent(db, workspace_id)
    else:
        raise HTTPException(status_code=404, detail="Agent not recognized")

@router.post("/orchestrate/full")
def run_full_workflow(
    product_id: Optional[str] = None,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    target_product_id = product_id
    if target_product_id:
        from app.models.entities import Product
        p = db.query(Product).filter(
            Product.workspace_id == workspace_id,
            (Product.id == target_product_id) | (Product.sku == target_product_id)
        ).first()
        if p:
            target_product_id = p.id
    else:
        from app.models.entities import Product
        first_prod = db.query(Product).filter(Product.workspace_id == workspace_id).first()
        if first_prod:
            target_product_id = first_prod.id
            
    return orchestrator.run_full_autonomous_workflow(db, workspace_id, target_product_id)

@router.get("/runs")
def list_agent_runs(
    limit: int = 50,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    return db.query(AgentRun).filter(AgentRun.workspace_id == workspace_id).order_by(AgentRun.created_at.desc()).limit(limit).all()

@router.get("/runs/{run_id}")
def get_agent_run_detail(
    run_id: str,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    run = db.query(AgentRun).filter(AgentRun.id == run_id, AgentRun.workspace_id == workspace_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return run
