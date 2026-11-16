import csv
import io
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_workspace_id
from app.models.entities import Product
from app.schemas.domain import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter()

@router.get("", response_model=List[ProductResponse])
def list_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.workspace_id == workspace_id)
    if search:
        query = query.filter((Product.name.ilike(f"%{search}%")) | (Product.sku.ilike(f"%{search}%")))
    if category:
        query = query.filter(Product.category == category)
    return query.order_by(Product.created_at.desc()).offset(offset).limit(limit).all()

@router.post("", response_model=ProductResponse)
def create_product(
    product_in: ProductCreate,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    existing = db.query(Product).filter(Product.workspace_id == workspace_id, Product.sku == product_in.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Product SKU '{product_in.sku}' already exists.")
        
    product = Product(
        workspace_id=workspace_id,
        sku=product_in.sku,
        name=product_in.name,
        category=product_in.category,
        description=product_in.description,
        price=product_in.price,
        currency=product_in.currency,
        brand=product_in.brand,
        attributes=product_in.attributes or {}
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id, Product.workspace_id == workspace_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    product_in: ProductUpdate,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id, Product.workspace_id == workspace_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    update_data = product_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(product, field, val)
        
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(
    product_id: str,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id, Product.workspace_id == workspace_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

@router.post("/import")
async def import_products_csv(
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
    
    for row_idx, row in enumerate(reader, start=1):
        try:
            sku = row.get("sku", "").strip()
            name = row.get("name", "").strip()
            if not sku or not name:
                errors.append({"row": row_idx, "error": "SKU and Name are mandatory"})
                continue
                
            price = float(row.get("price", 0))
            category = row.get("category", "").strip() or None
            description = row.get("description", "").strip() or None
            brand = row.get("brand", "").strip() or None
            
            raw_attrs = row.get("attributes", "{}")
            try:
                attributes = json.loads(raw_attrs) if isinstance(raw_attrs, str) and raw_attrs else {}
            except Exception:
                attributes = {}
                
            existing = db.query(Product).filter(Product.workspace_id == workspace_id, Product.sku == sku).first()
            if existing:
                existing.name = name
                existing.price = price
                existing.category = category
                existing.description = description
                existing.brand = brand
                existing.attributes = attributes
            else:
                p = Product(
                    workspace_id=workspace_id,
                    sku=sku,
                    name=name,
                    price=price,
                    category=category,
                    description=description,
                    brand=brand,
                    attributes=attributes
                )
                db.add(p)
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

@router.get("/export/csv")
def export_products_csv(
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    products = db.query(Product).filter(Product.workspace_id == workspace_id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["sku", "name", "category", "description", "price", "currency", "brand", "attributes"])
    
    for p in products:
        writer.writerow([
            p.sku,
            p.name,
            p.category or "",
            p.description or "",
            p.price,
            p.currency,
            p.brand or "",
            json.dumps(p.attributes or {})
        ])
        
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=products_export.csv"}
    )
