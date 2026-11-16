from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_workspace_id
from app.models.entities import MarketingCampaign
from app.schemas.domain import MarketingGenerateRequest, MarketingCampaignResponse
from app.orchestration.coordinator import orchestrator

router = APIRouter()

@router.get("/campaigns", response_model=List[MarketingCampaignResponse])
def list_campaigns(
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    return db.query(MarketingCampaign).filter(MarketingCampaign.workspace_id == workspace_id).order_by(MarketingCampaign.created_at.desc()).all()

@router.post("/generate")
def generate_campaign(
    request: MarketingGenerateRequest,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    target_product_id = request.product_id
    if target_product_id:
        from app.models.entities import Product
        p = db.query(Product).filter(
            Product.workspace_id == workspace_id,
            (Product.id == target_product_id) | (Product.sku == target_product_id)
        ).first()
        if p:
            target_product_id = p.id

    return orchestrator.run_marketing_agent(
        db=db,
        workspace_id=workspace_id,
        campaign_name=request.campaign_name,
        campaign_type=request.campaign_type,
        product_id=target_product_id,
        target_audience=request.target_audience
    )

@router.put("/campaigns/{campaign_id}")
def update_campaign(
    campaign_id: str,
    update_data: dict,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    campaign = db.query(MarketingCampaign).filter(MarketingCampaign.id == campaign_id, MarketingCampaign.workspace_id == workspace_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    for k, v in update_data.items():
        if hasattr(campaign, k):
            setattr(campaign, k, v)
            
    db.commit()
    db.refresh(campaign)
    return campaign
