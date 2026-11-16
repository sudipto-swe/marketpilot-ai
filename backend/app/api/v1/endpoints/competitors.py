import csv
import io
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_workspace_id
from app.models.entities import Competitor, CompetitorProduct, CompetitorPriceHistory, Product, PriceAlert

router = APIRouter()

@router.get("")
def list_competitors(
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    comps = db.query(Competitor).filter(Competitor.workspace_id == workspace_id).all()
    res = []
    for c in comps:
        res.append({
            "id": c.id,
            "name": c.name,
            "website": c.website,
            "tracked_products_count": len(c.competitor_products)
        })
    return res

@router.get("/prices")
def get_competitor_prices(
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    items = (
        db.query(CompetitorProduct)
        .join(Competitor)
        .join(Product)
        .filter(Competitor.workspace_id == workspace_id)
        .all()
    )
    res = []
    for item in items:
        our_price = item.product.price
        diff_pct = round(((item.current_price - our_price) / our_price) * 100, 2)
        res.append({
            "id": item.id,
            "competitor_name": item.competitor.name,
            "our_product_sku": item.product.sku,
            "our_product_name": item.product.name,
            "our_price": our_price,
            "competitor_product_name": item.competitor_product_name,
            "competitor_price": item.current_price,
            "currency": item.currency,
            "difference_pct": diff_pct,
            "last_updated": item.last_updated
        })
    return res

@router.get("/alerts")
def get_price_alerts(
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    return db.query(PriceAlert).filter(PriceAlert.workspace_id == workspace_id).order_by(PriceAlert.created_at.desc()).all()

@router.get("/dynamic-repricing/{sku}")
def get_sku_dynamic_repricing(
    sku: str,
    min_margin_pct: float = 20.0,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    from app.analytics.dynamic_repricer import calculate_dynamic_repricing
    prod = db.query(Product).filter(
        Product.workspace_id == workspace_id,
        (Product.sku == sku) | (Product.id == sku)
    ).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
        
    comp_prod = (
        db.query(CompetitorProduct)
        .join(Competitor)
        .filter(CompetitorProduct.product_id == prod.id)
        .first()
    )
    comp_price = comp_prod.current_price if comp_prod else prod.price
    
    # Unit cost estimation: 50% of original price or from attributes
    unit_cost = prod.attributes.get("unit_cost") if prod.attributes else None
    if not unit_cost:
        unit_cost = round(prod.price * 0.45, 2) # 55% gross margin baseline
        
    return calculate_dynamic_repricing(
        current_price=prod.price,
        competitor_price=comp_price,
        unit_cost=unit_cost,
        min_margin_pct=min_margin_pct
    )

@router.post("/import")
async def import_competitor_prices_csv(
    file: UploadFile = File(...),
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    content = await file.read()
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        decoded = content.decode("latin-1")
        
    reader = csv.DictReader(io.StringIO(decoded))
    imported = 0
    errors = []
    
    products = {p.sku: p for p in db.query(Product).filter(Product.workspace_id == workspace_id).all()}
    
    for row_idx, row in enumerate(reader, start=1):
        try:
            comp_name = row.get("competitor_name", "").strip()
            sku = row.get("product_sku", "").strip()
            comp_prod_name = row.get("competitor_product_name", "").strip()
            price = float(row.get("price", 0))
            
            if not comp_name or not sku or price <= 0:
                errors.append({"row": row_idx, "error": "Competitor name, product SKU and positive price are required"})
                continue
                
            if sku not in products:
                errors.append({"row": row_idx, "error": f"Product SKU '{sku}' not recognized"})
                continue
                
            # Find or create competitor
            comp = db.query(Competitor).filter(Competitor.workspace_id == workspace_id, Competitor.name == comp_name).first()
            if not comp:
                comp = Competitor(workspace_id=workspace_id, name=comp_name)
                db.add(comp)
                db.flush()
                
            # Find or create competitor product
            target_prod = products[sku]
            comp_prod = db.query(CompetitorProduct).filter(
                CompetitorProduct.competitor_id == comp.id,
                CompetitorProduct.product_id == target_prod.id
            ).first()
            
            if not comp_prod:
                comp_prod = CompetitorProduct(
                    competitor_id=comp.id,
                    product_id=target_prod.id,
                    competitor_product_name=comp_prod_name or target_prod.name,
                    current_price=price
                )
                db.add(comp_prod)
                db.flush()
            else:
                comp_prod.current_price = price
                comp_prod.competitor_product_name = comp_prod_name or comp_prod.competitor_product_name
                
            # Record price history
            history = CompetitorPriceHistory(
                competitor_product_id=comp_prod.id,
                price=price,
                source=row.get("source", "upload")
            )
            db.add(history)
            imported += 1
        except Exception as e:
            errors.append({"row": row_idx, "error": str(e)})
            
    db.commit()
    return {
        "status": "success",
        "imported_count": imported,
        "failed_count": len(errors),
        "errors": errors
    }
