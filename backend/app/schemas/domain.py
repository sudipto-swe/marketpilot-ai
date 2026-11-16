from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth
class Token(BaseModel):
    access_token: str
    token_type: str
    workspace_id: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    role: str
    workspace_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Product
class ProductBase(BaseModel):
    sku: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    price: float
    currency: str = "USD"
    brand: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    brand: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class ProductResponse(ProductBase):
    id: str
    workspace_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Review
class ReviewBase(BaseModel):
    product_sku: str
    rating: float
    review_text: str
    review_date: Optional[datetime] = None
    source: str = "direct"

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: str
    product_id: str
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    topics: List[str] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True

# Competitor Price
class CompetitorPriceBase(BaseModel):
    competitor_name: str
    product_sku: str
    competitor_product_name: str
    price: float
    currency: str = "USD"
    source: str = "demo"

class CompetitorPriceCreate(CompetitorPriceBase):
    pass

# AI Agent Output Base Schema (Contract Requirement)
class AgentOutputSchema(BaseModel):
    agent_name: str
    status: str
    summary: str
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float
    requires_human_approval: bool
    created_at: str

# SEO Content
class SEOGenerateRequest(BaseModel):
    product_id: str
    target_keywords: Optional[List[str]] = None

class SEOContentResponse(BaseModel):
    id: str
    product_id: str
    generated_title: str
    generated_description: str
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    bullet_points: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    faqs: List[Dict[str, str]] = Field(default_factory=list)
    alt_text: Optional[str] = None
    is_claim_validated: bool
    claim_validation_details: Dict[str, Any] = Field(default_factory=dict)
    approval_status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Marketing Campaign
class MarketingGenerateRequest(BaseModel):
    product_id: Optional[str] = None
    campaign_name: str
    campaign_type: str
    target_audience: Optional[str] = None

class MarketingCampaignResponse(BaseModel):
    id: str
    product_id: Optional[str] = None
    campaign_name: str
    campaign_type: str
    target_audience: Optional[str] = None
    strategy: Optional[str] = None
    facebook_caption: Optional[str] = None
    instagram_caption: Optional[str] = None
    ad_copy: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    ab_testing_variations: List[Dict[str, Any]] = Field(default_factory=list)
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Approvals
class ApprovalActionRequest(BaseModel):
    notes: Optional[str] = None
