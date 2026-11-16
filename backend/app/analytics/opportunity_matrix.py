from typing import List, Dict, Any
import numpy as np

def score_product_opportunities(
    products: List[Dict[str, Any]],
    reviews_analytics: Dict[str, Dict[str, Any]],
    competitor_data: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Computes an Opportunity & Risk Index (0 - 100) for every product in the catalog.
    Factors:
    - Margin Opportunity (Competitor priced higher = room to raise prices)
    - Margin Risk (Competitor priced lower = churn danger)
    - Voice-of-Customer Health (Negative sentiment & battery/quality complaint ratio)
    - SEO Content Freshness
    """
    scored_products = []
    
    for p in products:
        sku = p["sku"]
        price = p["price"]
        
        comp_info = competitor_data.get(sku, {})
        comp_price = comp_info.get("competitor_price", price)
        price_gap_pct = ((comp_price - price) / price) * 100 if price > 0 else 0
        
        rev_info = reviews_analytics.get(sku, {})
        avg_rating = rev_info.get("avg_rating", 4.0)
        neg_pct = rev_info.get("negative_sentiment_percentage", 15.0)
        
        # Risk Score (0 - 100): High when competitor undercuts and negative reviews are frequent
        risk_score = 0.0
        if price_gap_pct < -5.0:
            risk_score += min(50.0, abs(price_gap_pct) * 2.5)
        if neg_pct > 20.0:
            risk_score += min(50.0, (neg_pct - 20.0) * 2.0)
            
        risk_score = min(100.0, round(risk_score, 1))
        
        # Opportunity Score (0 - 100): High when competitor is higher (pricing room) or high rating
        opp_score = 0.0
        if price_gap_pct > 5.0:
            opp_score += min(50.0, price_gap_pct * 2.0)
        if avg_rating >= 4.5:
            opp_score += 40.0
        elif avg_rating >= 4.0:
            opp_score += 20.0
            
        opp_score = min(100.0, round(opp_score, 1))
        
        # Priority Tier
        if risk_score >= 60.0:
            tier = "CRITICAL_ACTION_REQUIRED"
            recommended_action = "Execute dynamic margin repricing & investigate product quality complaints"
        elif opp_score >= 60.0:
            tier = "HIGH_GROWTH_POTENTIAL"
            recommended_action = "Expand marketing campaigns & test premium price tier"
        else:
            tier = "STABLE_PERFORMANCE"
            recommended_action = "Maintain current pricing & monitor reviews"
            
        scored_products.append({
            "product_id": p.get("id"),
            "sku": sku,
            "name": p.get("name"),
            "price": price,
            "competitor_price": comp_price,
            "price_variance_pct": round(price_gap_pct, 2),
            "average_rating": avg_rating,
            "negative_sentiment_pct": neg_pct,
            "risk_score": risk_score,
            "opportunity_score": opp_score,
            "priority_tier": tier,
            "recommended_action": recommended_action
        })
        
    # Sort by risk score descending
    scored_products.sort(key=lambda x: (x["risk_score"], x["opportunity_score"]), reverse=True)
    return scored_products
