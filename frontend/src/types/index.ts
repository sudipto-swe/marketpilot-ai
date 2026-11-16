export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  workspace_id?: string;
}

export interface Product {
  id: string;
  sku: string;
  name: string;
  category?: string;
  description?: string;
  price: number;
  currency: string;
  brand?: string;
  attributes?: Record<string, any>;
  created_at: string;
}

export interface Review {
  id: string;
  product_sku: string;
  rating: number;
  review_text: string;
  sentiment?: string;
  sentiment_score?: number;
  topics?: string[];
  source?: string;
  created_at: string;
}

export interface CompetitorPrice {
  id: string;
  competitor_name: string;
  our_product_sku: string;
  our_product_name: string;
  our_price: number;
  competitor_product_name: string;
  competitor_price: number;
  currency: string;
  difference_pct: number;
  last_updated: string;
}

export interface PriceAlert {
  id: string;
  product_id: string;
  competitor_name: string;
  our_price: number;
  competitor_price: number;
  difference_percentage: number;
  alert_type: string;
  recommendation: string;
  status: string;
  created_at: string;
}

export interface AgentMeta {
  id: string;
  name: string;
  role: string;
  description: string;
  total_runs: number;
  last_run_time: string | null;
  last_status: string;
  last_summary: string;
}

export interface ApprovalItem {
  id: string;
  item_type: string;
  item_id: string;
  title: string;
  description: string;
  payload: Record<string, any>;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'REVISION_REQUESTED';
  created_at: string;
}

export interface DashboardStats {
  total_products: number;
  total_reviews: number;
  average_rating: number;
  positive_sentiment_percentage: number;
  negative_sentiment_percentage: number;
  active_price_alerts: number;
  pending_approvals: number;
  recent_agent_runs: Array<{
    id: string;
    agent_name: string;
    status: string;
    summary: string;
    created_at: string;
  }>;
  latest_business_insights: {
    summary: string;
    recommendations: any[];
  };
}
