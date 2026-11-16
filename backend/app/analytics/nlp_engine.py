import re
from typing import List, Dict, Any, Tuple
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

# Deterministic Sentiment Lexicons for E-commerce
POSITIVE_WORDS = {
    "great", "excellent", "amazing", "good", "love", "perfect", "awesome",
    "best", "fantastic", "quality", "durable", "fast", "reliable", "easy",
    "comfortable", "clear", "crisp", "long-lasting", "recommend", "satisfied",
    "outstanding", "impressive", "superb", "worth", "sturdy", "smooth"
}

NEGATIVE_WORDS = {
    "bad", "terrible", "horrible", "awful", "worst", "poor", "broken",
    "disappointing", "disappointed", "slow", "unreliable", "cheap", "flimsy",
    "hard", "uncomfortable", "noisy", "short", "died", "defect", "defective",
    "useless", "waste", "drain", "drains", "draining", "lag", "crash", "fails", "failed", "hate"
}

COMPLAINT_TOPICS = {
    "battery": ["battery", "charge", "charging", "charger", "drains", "power", "dead", "hours"],
    "sound_audio": ["sound", "audio", "noise", "bass", "volume", "microphone", "mic", "static"],
    "connectivity": ["bluetooth", "connect", "connection", "disconnect", "sync", "pairing", "range"],
    "build_quality": ["plastic", "cheap", "break", "broken", "durability", "snap", "hinge", "flimsy"],
    "comfort_fit": ["ear", "ears", "fit", "tight", "heavy", "pain", "hurt", "comfortable", "cushion"],
    "customer_service": ["service", "support", "warranty", "refund", "return", "shipping", "delivery"],
    "price_value": ["price", "expensive", "money", "overpriced", "worth", "cost"]
}

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    return ' '.join(text.split())

def calculate_review_sentiment(text: str, rating: float) -> Tuple[str, float]:
    """
    Combines rating baseline with deterministic lexical analysis.
    Returns (sentiment, score_between_-1_and_1).
    """
    cleaned = clean_text(text)
    words = cleaned.split()
    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
    
    # Rating influence: 1-2 is negative (-0.5), 3 is neutral (0), 4-5 is positive (+0.5)
    rating_score = (rating - 3.0) / 2.0
    
    total_eval = pos_count + neg_count
    lex_score = 0.0
    if total_eval > 0:
        lex_score = (pos_count - neg_count) / total_eval
        
    combined_score = round(0.5 * rating_score + 0.5 * lex_score, 2)
    
    if combined_score > 0.15:
        return "positive", combined_score
    elif combined_score < -0.15:
        return "negative", combined_score
    else:
        return "neutral", combined_score

def extract_topics(text: str) -> List[str]:
    cleaned = clean_text(text)
    words = set(cleaned.split())
    matched_topics = []
    for topic, keywords in COMPLAINT_TOPICS.items():
        if any(kw in words for kw in keywords):
            matched_topics.append(topic)
    return matched_topics

def analyze_reviews_dataset(reviews_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic Pandas and TF-IDF analysis of review corpus.
    Calculates exact distributions, complaint percentages, rating trends, and top terms.
    """
    if not reviews_data:
        return {
            "total_reviews": 0,
            "average_rating": 0.0,
            "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
            "complaint_breakdown": {},
            "top_keywords": [],
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
        
    df = pd.DataFrame(reviews_data)
    total_reviews = len(df)
    avg_rating = round(float(df['rating'].mean()), 2)
    
    # Sentiment distribution
    sentiment_counts = df['sentiment'].value_counts().to_dict()
    sent_dist = {
        "positive": int(sentiment_counts.get("positive", 0)),
        "neutral": int(sentiment_counts.get("neutral", 0)),
        "negative": int(sentiment_counts.get("negative", 0))
    }
    
    # Rating distribution
    rating_counts = df['rating'].round().astype(int).value_counts().to_dict()
    rating_dist = {r: int(rating_counts.get(r, 0)) for r in [1, 2, 3, 4, 5]}
    
    # Negative reviews complaint breakdown
    neg_df = df[df['sentiment'] == "negative"]
    total_neg = len(neg_df)
    complaints = Counter()
    for _, row in neg_df.iterrows():
        topics = row.get('topics') or []
        for t in topics:
            complaints[t] += 1
            
    complaint_breakdown = {}
    for topic, count in complaints.most_common():
        pct = round((count / total_neg * 100), 1) if total_neg > 0 else 0.0
        complaint_breakdown[topic] = {
            "count": count,
            "percentage": pct
        }
        
    # TF-IDF keyword extraction
    top_keywords = []
    try:
        texts = df['review_text'].dropna().tolist()
        if len(texts) >= 2:
            tfidf = TfidfVectorizer(stop_words='english', max_features=10)
            tfidf.fit(texts)
            top_keywords = list(tfidf.get_feature_names_out())
    except Exception:
        top_keywords = []
        
    return {
        "total_reviews": total_reviews,
        "average_rating": avg_rating,
        "sentiment_distribution": sent_dist,
        "sentiment_percentages": {
            k: round(v / total_reviews * 100, 1) if total_reviews > 0 else 0.0
            for k, v in sent_dist.items()
        },
        "rating_distribution": rating_dist,
        "total_negative_reviews": total_neg,
        "complaint_breakdown": complaint_breakdown,
        "top_keywords": top_keywords
    }
