import csv
import io
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_workspace_id
from app.models.entities import Review, Product
from app.schemas.domain import ReviewCreate, ReviewResponse
from app.analytics.nlp_engine import calculate_review_sentiment, extract_topics, analyze_reviews_dataset

router = APIRouter()

@router.get("", response_model=List[ReviewResponse])
def list_reviews(
    product_id: Optional[str] = None,
    sentiment: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    query = db.query(Review).filter(Review.workspace_id == workspace_id)
    if product_id:
        query = query.filter(Review.product_id == product_id)
    if sentiment:
        query = query.filter(Review.sentiment == sentiment)
    return query.order_by(Review.created_at.desc()).offset(offset).limit(limit).all()

@router.post("", response_model=ReviewResponse)
def create_review(
    review_in: ReviewCreate,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.workspace_id == workspace_id, Product.sku == review_in.product_sku).first()
    if not product:
        raise HTTPException(status_code=400, detail=f"No product with SKU '{review_in.product_sku}' found")
        
    sentiment, score = calculate_review_sentiment(review_in.review_text, review_in.rating)
    topics = extract_topics(review_in.review_text)
    
    review = Review(
        workspace_id=workspace_id,
        product_id=product.id,
        product_sku=product.sku,
        rating=review_in.rating,
        review_text=review_in.review_text,
        sentiment=sentiment,
        sentiment_score=score,
        topics=topics,
        review_date=review_in.review_date or datetime.utcnow(),
        source=review_in.source
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

@router.get("/analytics")
def get_review_analytics(
    product_id: Optional[str] = None,
    workspace_id: str = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    query = db.query(Review).filter(Review.workspace_id == workspace_id)
    if product_id:
        query = query.filter(Review.product_id == product_id)
    reviews = query.all()
    
    review_dicts = [
        {
            "id": r.id,
            "rating": r.rating,
            "review_text": r.review_text,
            "sentiment": r.sentiment,
            "topics": r.topics or []
        }
        for r in reviews
    ]
    return analyze_reviews_dataset(review_dicts)

@router.post("/import")
async def import_reviews_csv(
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
    
    # Cache products
    products = {p.sku: p.id for p in db.query(Product).filter(Product.workspace_id == workspace_id).all()}
    
    for row_idx, row in enumerate(reader, start=1):
        try:
            sku = row.get("product_sku", "").strip()
            if not sku or sku not in products:
                errors.append({"row": row_idx, "error": f"Product with SKU '{sku}' not found in workspace"})
                continue
                
            rating = float(row.get("rating", 5.0))
            text = row.get("review_text", "").strip()
            if not text:
                errors.append({"row": row_idx, "error": "Review text is required"})
                continue
                
            review_id_ext = row.get("review_id", "").strip() or None
            source = row.get("source", "upload").strip()
            
            sentiment, score = calculate_review_sentiment(text, rating)
            topics = extract_topics(text)
            
            r = Review(
                workspace_id=workspace_id,
                product_id=products[sku],
                product_sku=sku,
                review_id_external=review_id_ext,
                rating=rating,
                review_text=text,
                sentiment=sentiment,
                sentiment_score=score,
                topics=topics,
                source=source
            )
            db.add(r)
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
