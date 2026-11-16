from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_workspace_id, get_current_user
from app.models.entities import ApprovalRequest, ApprovalStatus, User, Product, PriceAlert, SEOContent, MarketingCampaign
from app.schemas.domain import ApprovalActionRequest

router = APIRouter()

@router.get("")
def list_approvals(
    status: Optional[str] = None,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    query = db.query(ApprovalRequest).filter(ApprovalRequest.workspace_id == workspace_id)
    if status:
        query = query.filter(ApprovalRequest.status == status)
    return query.order_by(ApprovalRequest.created_at.desc()).all()

@router.post("/{approval_id}/approve")
def approve_request(
    approval_id: str,
    action_in: Optional[ApprovalActionRequest] = None,
    current_user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id, ApprovalRequest.workspace_id == workspace_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
        
    approval.status = ApprovalStatus.APPROVED.value
    approval.reviewed_by_id = current_user.id
    approval.reviewed_at = datetime.now(timezone.utc)
    
    # Execute actual business logic based on approval type
    if approval.item_type == "PRICE_CHANGE":
        prod = db.query(Product).filter(Product.id == approval.item_id).first()
        if prod and "new_price" in approval.payload:
            prod.price = float(approval.payload["new_price"])
    elif approval.item_type == "SEO_CONTENT":
        seo = db.query(SEOContent).filter(SEOContent.id == approval.item_id).first()
        if seo:
            seo.approval_status = ApprovalStatus.APPROVED.value
    elif approval.item_type == "MARKETING_CAMPAIGN":
        camp = db.query(MarketingCampaign).filter(MarketingCampaign.id == approval.item_id).first()
        if camp:
            camp.status = ApprovalStatus.APPROVED.value
            
    db.commit()
    db.refresh(approval)
    return {
        "status": "success",
        "message": f"Approved {approval.item_type} successfully.",
        "approval": approval
    }

@router.post("/{approval_id}/reject")
def reject_request(
    approval_id: str,
    action_in: Optional[ApprovalActionRequest] = None,
    current_user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id, ApprovalRequest.workspace_id == workspace_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
        
    approval.status = ApprovalStatus.REJECTED.value
    approval.reviewed_by_id = current_user.id
    approval.reviewed_at = datetime.now(timezone.utc)
    approval.rejection_reason = action_in.notes if action_in else "Rejected by human reviewer"
    
    db.commit()
    db.refresh(approval)
    return {
        "status": "success",
        "message": f"Rejected {approval.item_type}.",
        "approval": approval
    }
