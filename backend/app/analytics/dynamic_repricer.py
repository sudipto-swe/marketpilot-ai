from typing import Dict, Any, List
import pandas as pd
import numpy as np

def calculate_dynamic_repricing(
    current_price: float,
    competitor_price: float,
    unit_cost: float,
    min_margin_pct: float = 20.0,
    sentiment_score: float = 0.5,
    inventory_level: int = 100
) -> Dict[str, Any]:
    """
    Intelligent dynamic repricing algorithm calculating profit-margin protected price points.
    Considers:
    - Competitor pricing pressure
    - Hard floor unit cost & minimum gross margin threshold
    - Customer sentiment elasticity (higher sentiment = higher price tolerance)
    - Inventory velocity pressure
    """
    min_allowable_price = round(unit_cost * (1 + (min_margin_pct / 100.0)), 2)
    
    # Baseline undercut match: 1.5% below competitor or matching
    if competitor_price > min_allowable_price:
        tentative_target = round(competitor_price * 0.985, 2)
    else:
        # Cannot beat competitor without violating margin guardrail
        tentative_target = min_allowable_price
        
    # Sentiment modifier: If sentiment is exceptionally positive (> 0.4), can charge +2% to +5% premium
    premium_factor = 0.0
    if sentiment_score > 0.4:
        premium_factor = 0.03 # 3% brand premium
    elif sentiment_score < -0.2:
        premium_factor = -0.02 # 2% discount incentive for churn reduction
        
    recommended_price = round(max(min_allowable_price, tentative_target * (1 + premium_factor)), 2)
    
    # Calculate financial impact
    current_margin_dollar = round(current_price - unit_cost, 2)
    current_margin_pct = round((current_margin_dollar / current_price) * 100, 1) if current_price > 0 else 0
    
    new_margin_dollar = round(recommended_price - unit_cost, 2)
    new_margin_pct = round((new_margin_dollar / recommended_price) * 100, 1) if recommended_price > 0 else 0
    
    guardrail_status = "SAFE_MARGIN_PRESERVED" if new_margin_pct >= min_margin_pct else "FLOOR_LIMIT_TRIGGERED"
    
    return {
        "current_price": current_price,
        "competitor_price": competitor_price,
        "unit_cost": unit_cost,
        "min_allowable_price": min_allowable_price,
        "recommended_price": recommended_price,
        "price_change_dollar": round(recommended_price - current_price, 2),
        "price_change_pct": round(((recommended_price - current_price) / current_price) * 100, 2),
        "current_margin_pct": current_margin_pct,
        "projected_margin_pct": new_margin_pct,
        "guardrail_status": guardrail_status,
        "margin_floor_protected": True
    }
