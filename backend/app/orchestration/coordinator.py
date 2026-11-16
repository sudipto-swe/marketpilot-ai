from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.agents.specialized_agents import (
    ReviewAnalysisAgent,
    CompetitorPriceAgent,
    SEOContentAgent,
    MarketingCampaignAgent,
    BusinessInsightsAgent
)

class MultiAgentOrchestrator:
    """
    CrewAI-compatible multi-agent orchestrator coordinating sequential or parallel runs
    of specialized business agents, collecting traceable evidence, and persisting execution runs.
    """
    def __init__(self):
        self.review_agent = ReviewAnalysisAgent()
        self.price_agent = CompetitorPriceAgent()
        self.seo_agent = SEOContentAgent()
        self.marketing_agent = MarketingCampaignAgent()
        self.insights_agent = BusinessInsightsAgent()

    def run_review_agent(self, db: Session, workspace_id: str, product_id: str = None) -> Dict[str, Any]:
        return self.review_agent.run(db, workspace_id, product_id)

    def run_price_agent(self, db: Session, workspace_id: str) -> Dict[str, Any]:
        return self.price_agent.run(db, workspace_id)

    def run_seo_agent(self, db: Session, workspace_id: str, product_id: str) -> Dict[str, Any]:
        return self.seo_agent.run(db, workspace_id, product_id)

    def run_marketing_agent(self, db: Session, workspace_id: str, campaign_name: str, campaign_type: str, product_id: str = None, target_audience: str = None) -> Dict[str, Any]:
        return self.marketing_agent.run(db, workspace_id, campaign_name, campaign_type, product_id, target_audience)

    def run_insights_agent(self, db: Session, workspace_id: str) -> Dict[str, Any]:
        return self.insights_agent.run(db, workspace_id)

    def run_full_autonomous_workflow(self, db: Session, workspace_id: str, sample_product_id: str = None) -> Dict[str, Any]:
        """
        Executes an end-to-end multi-agent orchestration pipeline:
        1. Review Analysis
        2. Competitor Price Monitoring
        3. SEO Content Generation (if sample_product_id present)
        4. Marketing Campaign Draft
        5. Business Insights Synthesis
        """
        results = {}
        # 1. Review Analysis
        results["review_analysis"] = self.review_agent.run(db, workspace_id, sample_product_id)
        
        # 2. Competitor Price Monitoring
        results["price_monitoring"] = self.price_agent.run(db, workspace_id)
        
        # 3. SEO Content Generation
        if sample_product_id:
            results["seo_generation"] = self.seo_agent.run(db, workspace_id, sample_product_id)
            
        # 4. Marketing Campaign Draft
        results["marketing_campaign"] = self.marketing_agent.run(
            db, workspace_id,
            campaign_name="Autonomous Growth Sprint",
            campaign_type="omnichannel_promotional",
            product_id=sample_product_id,
            target_audience="High-intent online shoppers"
        )
        
        # 5. Business Insights Synthesis
        results["business_insights"] = self.insights_agent.run(db, workspace_id)
        
        return {
            "status": "success",
            "message": "Full multi-agent workflow executed successfully.",
            "pipeline_stages": list(results.keys()),
            "results": results
        }

orchestrator = MultiAgentOrchestrator()
