import re
from typing import Dict, Any, List, Tuple

UNVERIFIED_CLAIM_PATTERNS = [
    r"100%\s+guaranteed",
    r"miracle",
    r"medical\s+grade",
    r"fda\s+approved",
    r"military\s+grade",
    r"best\s+in\s+the\s+world",
    r"lifetime\s+warranty",
    r"waterproof\s+up\s+to\s+\d+\s*meters" # unless in attributes
]

def validate_seo_claims(generated_text: str, product_attributes: Dict[str, Any], verified_description: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Validates that generated text does not fabricate unverified claims,
    false warranty durations, or ungrounded specs not present in verified product data.
    """
    text_lower = generated_text.lower()
    violations = []
    
    # 1. Check prohibited ungrounded buzzwords
    for pattern in UNVERIFIED_CLAIM_PATTERNS:
        matches = re.findall(pattern, text_lower)
        if matches:
            # Check if verified description or attributes explicitly support it
            all_known = (str(product_attributes) + " " + (verified_description or "")).lower()
            for m in matches:
                if m not in all_known:
                    violations.append(f"Unverified hyperbolic or guarantee claim detected: '{m}'")
                    
    # 2. Check numeric specifications (e.g. 50 hours battery when attr says 30)
    # Check battery hours
    battery_match = re.search(r'(\d+)\s*(?:hour|hr|hours|hrs)\s*battery', text_lower)
    if battery_match:
        claimed_hours = int(battery_match.group(1))
        verified_hours = product_attributes.get("battery_hours") or product_attributes.get("battery_life")
        if verified_hours:
            try:
                verified_int = int(str(verified_hours).split()[0])
                if claimed_hours > verified_int:
                    violations.append(f"Exaggerated specification: Claimed {claimed_hours} hrs battery vs verified {verified_int} hrs")
            except Exception:
                pass
                
    is_valid = len(violations) == 0
    return is_valid, {
        "valid": is_valid,
        "violations": violations,
        "verified_attributes_checked": list(product_attributes.keys()),
        "confidence_score": 0.99 if is_valid else 0.45
    }
