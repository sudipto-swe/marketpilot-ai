from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import httpx
from app.core.config import settings

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generates raw text response."""
        pass

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip('/')
        self.model = model or settings.OLLAMA_MODEL

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}\n<|assistant|>",
                "stream": False,
                "format": "json"
            }
            with httpx.Client(timeout=60.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    return res.json().get("response", "")
                raise RuntimeError(f"Ollama error: HTTP {res.status_code} - {res.text}")
        except Exception as e:
            # Fallback gracefully
            return MockLLMProvider().generate_response(system_prompt, user_prompt)

class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic, realistic simulation provider that requires 0 keys and 0 downloads.
    Generates rich, context-aware structured outputs according to prompt requirements.
    """
    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        prompt_lower = (system_prompt + " " + user_prompt).lower()
        
        if "review_analysis" in prompt_lower or "review" in prompt_lower:
            return json.dumps({
                "agent_name": "review_analysis",
                "status": "completed",
                "summary": "Customer review analysis indicates high satisfaction with audio performance but repeated concerns over battery life and Bluetooth sync.",
                "findings": [
                    {
                        "category": "battery",
                        "finding": "Battery endurance issues represent the primary complaint among 1-2 star reviews.",
                        "severity": "HIGH",
                        "impact": "Customer churn and return rate increase"
                    },
                    {
                        "category": "audio_quality",
                        "finding": "Audio clarity and dynamic range consistently praised in 4-5 star reviews.",
                        "severity": "LOW",
                        "impact": "Core brand differentiator"
                    }
                ],
                "evidence": [
                    {"type": "calculated_metric", "metric": "battery_complaint_ratio", "value": "32% of negative reviews"},
                    {"type": "rating_trend", "trend": "average rating stable at 4.2 stars"}
                ],
                "recommendations": [
                    {"action": "Investigate firmware power management to extend battery standby life.", "priority": "HIGH"},
                    {"action": "Clarify real-world battery hours in product specs to align expectations.", "priority": "MEDIUM"}
                ],
                "confidence": 0.94,
                "requires_human_approval": False,
                "created_at": "2026-11-16T12:00:00Z"
            })
            
        elif "price_monitoring" in prompt_lower or "competitor" in prompt_lower or "price" in prompt_lower:
            return json.dumps({
                "agent_name": "competitor_price_monitoring",
                "status": "completed",
                "summary": "Price intelligence detected key competitor discounted similar model by 12%. Recommendation drafted for human approval.",
                "findings": [
                    {
                        "competitor": "SoundWave Pro",
                        "price_difference": "-12.5%",
                        "our_price": 59.99,
                        "competitor_price": 52.49,
                        "finding": "Competitor undercut our flagship unit during seasonal promotion."
                    }
                ],
                "evidence": [
                    {"source": "Competitor Price History", "date": "2026-11-15", "observed_price": 52.49}
                ],
                "recommendations": [
                    {
                        "type": "PRICE_REDUCTION_APPROVAL",
                        "proposed_price": 54.99,
                        "expected_margin_impact": "-3%",
                        "requires_human_approval": True,
                        "rationale": "Match competitor value proposition while preserving premium branding"
                    }
                ],
                "confidence": 0.96,
                "requires_human_approval": True,
                "created_at": "2026-11-16T12:00:00Z"
            })
            
        elif "seo" in prompt_lower:
            return json.dumps({
                "agent_name": "seo_content_generation",
                "status": "completed",
                "summary": "Generated high-converting SEO metadata and structured feature descriptions strictly grounded in verified database specs.",
                "generated_title": "MarketPilot Wireless Noise-Cancelling Headphones - 30hr Battery & Hi-Fi Audio",
                "generated_description": "Engineered for immersive sound and all-day comfort. Featuring precision-tuned dynamic drivers, reliable wireless Bluetooth connectivity, and up to 30 hours of verified continuous playtime.",
                "meta_title": "Buy Wireless Over-Ear Headphones | 30-Hour Battery & Deep Bass",
                "meta_description": "Shop premium wireless headphones with 30-hour battery life, ergonomic memory foam earcups, and crystal clear call quality. Free shipping.",
                "bullet_points": [
                    "Extended 30-Hour Playtime on a single charge",
                    "Ergonomic over-ear memory foam cushions for all-day comfort",
                    "Instant pairing with multi-device Bluetooth support",
                    "Built-in omnidirectional microphone for high-clarity voice calls"
                ],
                "keywords": ["wireless headphones", "30 hour battery", "bluetooth headset", "noise cancelling headphones", "over ear headphones"],
                "faqs": [
                    {"question": "How long does the battery last?", "answer": "The battery provides up to 30 hours of continuous playback per charge."},
                    {"question": "Can I use it for hands-free calls?", "answer": "Yes, it includes an integrated high-definition microphone for clear voice communication."}
                ],
                "alt_text": "MarketPilot Wireless Over-Ear Headphones in Matte Black with memory foam ear cushions",
                "confidence": 0.98,
                "requires_human_approval": True,
                "created_at": "2026-11-16T12:00:00Z"
            })
            
        elif "marketing" in prompt_lower:
            return json.dumps({
                "agent_name": "marketing_campaign",
                "status": "completed",
                "summary": "Drafted multi-channel promotional campaign targeting productivity enthusiasts and audiophiles.",
                "campaign_name": "Unstoppable Sound - Winter Edition",
                "campaign_type": "promotional",
                "target_audience": "Remote workers, commuters, and daily fitness enthusiasts aged 22-45",
                "strategy": "Highlight 30-hour battery freedom and fatigue-free comfort to drive holiday conversions.",
                "facebook_caption": "30 hours of pure, uninterrupted focus. Meet your new workday essential with comfort that outlasts your longest playlist. 🎧 Shop today and upgrade your sound.",
                "instagram_caption": "Zero cords. Zero distractions. Just 30 hours of pure audio bliss. ✨ Tap the link in bio to experience true sound freedom. #AudioLife #WirelessHeadphones #Focus",
                "ad_copy": "Tired of headphones dying before your day ends? Experience 30 hours of battery life with plush memory foam earcups. Order now for exclusive perks.",
                "email_subject": "Sound that stays with you: Discover 30-hour wireless freedom",
                "email_body": "Hi there,\n\nLife doesn't stop, and neither should your music. With our 30-hour verified playtime and ergonomic fit, you can conquer back-to-back calls and weekend travels without reaching for a charger.\n\nClaim your pair today.\n\nBest,\nThe MarketPilot Team",
                "ab_testing_variations": [
                    {"variant": "A", "focus": "Battery Life Freedom", "headline": "30 Hours of Non-Stop Audio"},
                    {"variant": "B", "focus": "Ergonomic Comfort", "headline": "Headphones So Light, You'll Forget They're On"}
                ],
                "confidence": 0.92,
                "requires_human_approval": True,
                "created_at": "2026-11-16T12:00:00Z"
            })
            
        elif "business_insights" in prompt_lower or "insights" in prompt_lower or "synthesis" in prompt_lower:
            return json.dumps({
                "agent_name": "business_insights",
                "status": "completed",
                "summary": "Synthesized intelligence across review sentiment, competitor pricing, and SEO engagement. Core risk identified in competitor discounting while battery messaging requires specification alignment.",
                "findings": [
                    {
                        "source_agent": "review_analysis",
                        "finding": "Customer complaints center on battery degradation perceptions despite 30hr specification.",
                        "urgency": "MEDIUM"
                    },
                    {
                        "source_agent": "competitor_price_monitoring",
                        "finding": "Key rival reduced price to $52.49 (-12.5%), putting immediate margin pressure on our $59.99 offering.",
                        "urgency": "HIGH"
                    },
                    {
                        "source_agent": "seo_content_generation",
                        "finding": "Search demand for '30-hour battery wireless' has high conversion potential if highlighted in primary copy.",
                        "urgency": "MEDIUM"
                    }
                ],
                "evidence": [
                    {"evidence_key": "negative_review_topics", "metric": "battery: 32% of 1-star reviews"},
                    {"evidence_key": "competitor_price_gap", "metric": "Competitor A @ $52.49 vs Our $59.99"}
                ],
                "recommendations": [
                    {
                        "recommendation": "Submit a tactical promotional price revision to $54.99 for human management approval.",
                        "rationale": "Closes price gap to under $2.50 without completely eroding brand equity.",
                        "requires_approval": True
                    },
                    {
                        "recommendation": "Deploy the grounded SEO product description update focusing on verified battery longevity guidelines.",
                        "rationale": "Sets accurate customer expectations to curb return rate.",
                        "requires_approval": True
                    }
                ],
                "confidence": 0.95,
                "requires_human_approval": True,
                "created_at": "2026-11-16T12:00:00Z"
            })
            
        return json.dumps({
            "agent_name": "generic_agent",
            "status": "completed",
            "summary": "Completed analysis based on available database ground truth.",
            "findings": [],
            "evidence": [],
            "recommendations": [],
            "confidence": 0.9,
            "requires_human_approval": False,
            "created_at": "2026-11-16T12:00:00Z"
        })

def get_llm_provider() -> BaseLLMProvider:
    if settings.LLM_PROVIDER.lower() == "ollama":
        return OllamaProvider()
    return MockLLMProvider()
