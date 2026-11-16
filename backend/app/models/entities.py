from datetime import datetime, timezone
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum
)
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"

class ApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVISION_REQUESTED = "REVISION_REQUESTED"
    ARCHIVED = "ARCHIVED"

class AgentStatus(str, enum.Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default=UserRole.MEMBER.value, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    
    workspaces = relationship("WorkspaceMember", back_populates="user", cascade="all, delete-orphan")
    approvals_requested = relationship("ApprovalRequest", foreign_keys="ApprovalRequest.requested_by_id", back_populates="requested_by")
    approvals_reviewed = relationship("ApprovalRequest", foreign_keys="ApprovalRequest.reviewed_by_id", back_populates="reviewed_by")

class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=utc_now)
    
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="workspace", cascade="all, delete-orphan")
    competitors = relationship("Competitor", back_populates="workspace", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="workspace", cascade="all, delete-orphan")
    approval_requests = relationship("ApprovalRequest", back_populates="workspace", cascade="all, delete-orphan")

class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), default="member")
    created_at = Column(DateTime, default=utc_now)
    
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspaces")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    sku = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    brand = Column(String(100), nullable=True)
    attributes = Column(JSON, default=dict) # e.g. {"battery_hours": 30, "waterproof": "IPX7"}
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    
    workspace = relationship("Workspace", back_populates="products")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    competitor_products = relationship("CompetitorProduct", back_populates="product", cascade="all, delete-orphan")
    seo_contents = relationship("SEOContent", back_populates="product", cascade="all, delete-orphan")
    campaigns = relationship("MarketingCampaign", back_populates="product", cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    product_sku = Column(String(100), nullable=False, index=True)
    review_id_external = Column(String(100), nullable=True, index=True)
    rating = Column(Float, nullable=False)
    review_text = Column(Text, nullable=False)
    sentiment = Column(String(20), nullable=True) # positive, negative, neutral
    sentiment_score = Column(Float, nullable=True) # -1.0 to 1.0
    topics = Column(JSON, default=list) # e.g. ["battery", "sound", "comfort"]
    review_date = Column(DateTime, default=utc_now)
    source = Column(String(100), default="direct") # demo, upload, etc.
    created_at = Column(DateTime, default=utc_now)
    
    product = relationship("Product", back_populates="reviews")

class Competitor(Base):
    __tablename__ = "competitors"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    website = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    
    workspace = relationship("Workspace", back_populates="competitors")
    competitor_products = relationship("CompetitorProduct", back_populates="competitor", cascade="all, delete-orphan")

class CompetitorProduct(Base):
    __tablename__ = "competitor_products"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    competitor_id = Column(String(36), ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    competitor_product_name = Column(String(255), nullable=False)
    current_price = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    last_updated = Column(DateTime, default=utc_now)
    
    competitor = relationship("Competitor", back_populates="competitor_products")
    product = relationship("Product", back_populates="competitor_products")
    price_history = relationship("CompetitorPriceHistory", back_populates="competitor_product", cascade="all, delete-orphan")

class CompetitorPriceHistory(Base):
    __tablename__ = "competitor_price_history"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    competitor_product_id = Column(String(36), ForeignKey("competitor_products.id", ondelete="CASCADE"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    recorded_at = Column(DateTime, default=utc_now)
    source = Column(String(100), default="demo")
    
    competitor_product = relationship("CompetitorProduct", back_populates="price_history")

class PriceAlert(Base):
    __tablename__ = "price_alerts"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    competitor_name = Column(String(255), nullable=False)
    our_price = Column(Float, nullable=False)
    competitor_price = Column(Float, nullable=False)
    difference_percentage = Column(Float, nullable=False)
    alert_type = Column(String(50), nullable=False) # e.g. "COMPETITOR_LOWER", "COMPETITOR_HIGHER"
    recommendation = Column(Text, nullable=True)
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=utc_now)

class SEOContent(Base):
    __tablename__ = "seo_contents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    original_title = Column(String(255), nullable=True)
    original_description = Column(Text, nullable=True)
    generated_title = Column(String(255), nullable=False)
    generated_description = Column(Text, nullable=False)
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    bullet_points = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    faqs = Column(JSON, default=list)
    alt_text = Column(String(255), nullable=True)
    is_claim_validated = Column(Boolean, default=False)
    claim_validation_details = Column(JSON, default=dict)
    approval_status = Column(String(50), default=ApprovalStatus.PENDING.value)
    created_at = Column(DateTime, default=utc_now)
    
    product = relationship("Product", back_populates="seo_contents")

class MarketingCampaign(Base):
    __tablename__ = "marketing_campaigns"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    campaign_name = Column(String(255), nullable=False)
    campaign_type = Column(String(100), nullable=False) # seasonal, promo, retargeting
    target_audience = Column(String(255), nullable=True)
    strategy = Column(Text, nullable=True)
    facebook_caption = Column(Text, nullable=True)
    instagram_caption = Column(Text, nullable=True)
    ad_copy = Column(Text, nullable=True)
    email_subject = Column(String(255), nullable=True)
    email_body = Column(Text, nullable=True)
    ab_testing_variations = Column(JSON, default=list)
    status = Column(String(50), default="DRAFT") # DRAFT, PENDING_APPROVAL, APPROVED, REJECTED
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    
    product = relationship("Product", back_populates="campaigns")

class AgentRun(Base):
    __tablename__ = "agent_runs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False, index=True) # review_analysis, price_monitoring, seo_generator, marketing_campaign, business_insights, full_crew
    status = Column(String(50), default=AgentStatus.RUNNING.value)
    summary = Column(Text, nullable=True)
    findings = Column(JSON, default=list)
    evidence = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    confidence = Column(Float, default=0.0)
    requires_human_approval = Column(Boolean, default=False)
    input_params = Column(JSON, default=dict)
    execution_time_ms = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    
    workspace = relationship("Workspace", back_populates="agent_runs")

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    item_type = Column(String(50), nullable=False) # SEO_CONTENT, MARKETING_CAMPAIGN, PRICE_CHANGE, BUSINESS_INSIGHT
    item_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    payload = Column(JSON, default=dict)
    status = Column(String(50), default=ApprovalStatus.PENDING.value, index=True)
    requested_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    
    workspace = relationship("Workspace", back_populates="approval_requests")
    requested_by = relationship("User", foreign_keys=[requested_by_id], back_populates="approvals_requested")
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id], back_populates="approvals_reviewed")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="INFO") # INFO, WARNING, SUCCESS, ALERT
    is_read = Column(Boolean, default=False)
    link = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now)
