from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_workspace_id
from app.models.entities import SEOContent, Product, ApprovalRequest
from app.schemas.domain import SEOGenerateRequest, SEOContentResponse
from app.orchestration.coordinator import orchestrator
from app.validators.claim_validator import validate_seo_claims

router = APIRouter()

@router.get("/contents", response_model=List[SEOContentResponse])
def list_seo_contents(
    product_id: Optional[str] = None,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    query = db.query(SEOContent).filter(SEOContent.workspace_id == workspace_id)
    if product_id:
        query = query.filter(SEOContent.product_id == product_id)
    return query.order_by(SEOContent.created_at.desc()).all()

@router.post("/generate")
def generate_seo_content(
    request: SEOGenerateRequest,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    target_product_id = request.product_id
    from app.models.entities import Product
    p = db.query(Product).filter(
        Product.workspace_id == workspace_id,
        (Product.id == target_product_id) | (Product.sku == target_product_id)
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Target product not found")
        
    return orchestrator.run_seo_agent(db, workspace_id, p.id)

@router.post("/validate")
def validate_content(
    product_id: str,
    text_to_validate: str,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    from app.models.entities import Product
    product = db.query(Product).filter(
        Product.workspace_id == workspace_id,
        (Product.id == product_id) | (Product.sku == product_id)
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    is_valid, details = validate_seo_claims(text_to_validate, product.attributes or {}, product.description or "")
    return {
        "is_valid": is_valid,
        "details": details
    }
