from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.deps import get_current_workspace_id
from app.models.entities import Product, Review, PriceAlert, ApprovalRequest, AgentRun, ApprovalStatus
from app.orchestration.coordinator import orchestrator

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    total_products = db.query(Product).filter(Product.workspace_id == workspace_id).count()
    total_reviews = db.query(Review).filter(Review.workspace_id == workspace_id).count()
    
    avg_rating = db.query(func.avg(Review.rating)).filter(Review.workspace_id == workspace_id).scalar() or 0.0
    
    pos_reviews = db.query(Review).filter(Review.workspace_id == workspace_id, Review.sentiment == "positive").count()
    neg_reviews = db.query(Review).filter(Review.workspace_id == workspace_id, Review.sentiment == "negative").count()
    
    pos_pct = round((pos_reviews / total_reviews * 100), 1) if total_reviews > 0 else 0.0
    neg_pct = round((neg_reviews / total_reviews * 100), 1) if total_reviews > 0 else 0.0
    
    active_alerts = db.query(PriceAlert).filter(PriceAlert.workspace_id == workspace_id, PriceAlert.status == "ACTIVE").count()
    pending_approvals = db.query(ApprovalRequest).filter(ApprovalRequest.workspace_id == workspace_id, ApprovalRequest.status == ApprovalStatus.PENDING.value).count()
    
    recent_runs = (
        db.query(AgentRun)
        .filter(AgentRun.workspace_id == workspace_id)
        .order_by(AgentRun.created_at.desc())
        .limit(5)
        .all()
    )
    
    latest_insights = (
        db.query(AgentRun)
        .filter(AgentRun.workspace_id == workspace_id, AgentRun.agent_name == "business_insights")
        .order_by(AgentRun.created_at.desc())
        .first()
    )
    
    return {
        "total_products": total_products,
        "total_reviews": total_reviews,
        "average_rating": round(float(avg_rating), 2),
        "positive_sentiment_percentage": pos_pct,
        "negative_sentiment_percentage": neg_pct,
        "active_price_alerts": active_alerts,
        "pending_approvals": pending_approvals,
        "recent_agent_runs": [
            {
                "id": r.id,
                "agent_name": r.agent_name,
                "status": r.status,
                "summary": r.summary,
                "created_at": r.created_at
            }
            for r in recent_runs
        ],
        "latest_business_insights": {
            "summary": latest_insights.summary if latest_insights else "No synthesis run generated yet.",
            "recommendations": latest_insights.recommendations if latest_insights else []
        }
    }

@router.post("/generate")
def generate_insights(
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    return orchestrator.run_insights_agent(db, workspace_id)

@router.get("/opportunity-matrix")
def get_opportunity_matrix(
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    from app.analytics.opportunity_matrix import score_product_opportunities
    from app.models.entities import CompetitorProduct
    
    prods = db.query(Product).filter(Product.workspace_id == workspace_id).all()
    prod_dicts = [{"id": p.id, "sku": p.sku, "name": p.name, "price": p.price} for p in prods]
    
    # Aggregate review stats per SKU
    reviews = db.query(Review).filter(Review.workspace_id == workspace_id).all()
    review_stats = {}
    for r in reviews:
        if r.product_sku not in review_stats:
            review_stats[r.product_sku] = {"ratings": [], "sentiments": []}
        review_stats[r.product_sku]["ratings"].append(r.rating)
        review_stats[r.product_sku]["sentiments"].append(r.sentiment)
        
    reviews_formatted = {}
    for sku, data in review_stats.items():
        total = len(data["ratings"])
        avg_r = round(sum(data["ratings"]) / total, 2) if total > 0 else 0
        neg_count = sum(1 for s in data["sentiments"] if s == "negative")
        reviews_formatted[sku] = {
            "avg_rating": avg_r,
            "negative_sentiment_percentage": round((neg_count / total * 100), 1) if total > 0 else 0
        }
        
    # Aggregate competitor benchmarks
    comp_products = db.query(CompetitorProduct).join(Product).filter(Product.workspace_id == workspace_id).all()
    comp_data = {}
    for cp in comp_products:
        comp_data[cp.product.sku] = {
            "competitor_price": cp.current_price,
            "competitor_name": cp.competitor.name
        }
        
    return score_product_opportunities(prod_dicts, reviews_formatted, comp_data)
