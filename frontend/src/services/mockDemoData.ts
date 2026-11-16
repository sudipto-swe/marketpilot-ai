// Mock client-side dataset for standalone 24/7 web demonstration (GitHub Pages)
export const mockDemoData = {
  stats: {
    total_products: 3,
    total_reviews: 12,
    average_rating: 4.1,
    positive_sentiment_percentage: 66.7,
    negative_sentiment_percentage: 25.0,
    active_price_alerts: 2,
    pending_approvals: 3,
    recent_agent_runs: [
      {
        id: "run-rev-101",
        agent_name: "review_analysis",
        status: "completed",
        summary: "Analyzed 12 customer reviews. Repeated battery drainage identified in 32% of negative reviews.",
        created_at: new Date().toISOString()
      },
      {
        id: "run-price-102",
        agent_name: "competitor_price_monitoring",
        status: "completed",
        summary: "SoundWave Pro undercut HP001 by 12.5%. Dynamic margin guardrail safe repricing drafted.",
        created_at: new Date().toISOString()
      },
      {
        id: "run-seo-103",
        agent_name: "seo_content_generation",
        status: "completed",
        summary: "Generated search-optimized metadata for HP001. Claim validation passed 100%.",
        created_at: new Date().toISOString()
      }
    ],
    latest_business_insights: {
      summary: "Multi-agent synthesis across voice-of-customer, competitor price moves, and SEO opportunities. Immediate margin protection recommended on flagship inventory.",
      recommendations: [
        {
          action: "Approve proposed price revision to $53.25 for HP001 to recover sales volume while preserving 54.8% gross margin.",
          rationale: "Closes competitive gap with SoundWave Pro while strictly protecting the $24.09 COGS floor.",
          requires_approval: true
        },
        {
          action: "Deploy grounded SEO copy highlighting 30-hour verified battery life.",
          rationale: "Aligns customer expectations to curb return rate.",
          requires_approval: true
        }
      ]
    }
  },
  products: [
    {
      id: "492b25aa-62e0-4a7e-a6e3-471e51ffdf2a",
      sku: "HP001",
      name: "MarketPilot Studio Over-Ear Wireless Headphones",
      category: "Audio",
      description: "High-fidelity wireless studio headphones featuring precision dynamic drivers and ergonomic memory foam cushions.",
      price: 53.54,
      currency: "USD",
      brand: "MarketPilot",
      attributes: { battery_hours: 30, driver_size: "40mm", bluetooth: "5.3", weight_grams: 240, unit_cost: 24.09 },
      created_at: new Date().toISOString()
    },
    {
      id: "7dba7ae3-b564-45d3-b657-23d8cddd229c",
      sku: "SPK002",
      name: "MarketPilot SoundPulse Waterproof Bluetooth Speaker",
      category: "Audio",
      description: "Ultra-portable rugged wireless speaker designed for outdoor adventures with deep bass radiators.",
      price: 35.69,
      currency: "USD",
      brand: "MarketPilot",
      attributes: { waterproof_rating: "IPX7", battery_hours: 16, output_watts: 20, unit_cost: 16.06 },
      created_at: new Date().toISOString()
    },
    {
      id: "2f5e9008-5fa0-4e09-ade4-a21a1770a8b9",
      sku: "WCH003",
      name: "MarketPilot PulseFit Fitness Smartwatch",
      category: "Wearables",
      description: "Comprehensive health tracking smartwatch featuring continuous heart rate, sleep stages, and workout tracking.",
      price: 79.99,
      currency: "USD",
      brand: "MarketPilot",
      attributes: { screen_type: "AMOLED 1.4 inch", battery_days: 7, water_resistance: "5ATM", unit_cost: 36.00 },
      created_at: new Date().toISOString()
    }
  ],
  matrix: [
    {
      product_id: "492b25aa-62e0-4a7e-a6e3-471e51ffdf2a",
      sku: "HP001",
      name: "MarketPilot Studio Over-Ear Wireless Headphones",
      price: 53.54,
      competitor_price: 52.49,
      price_variance_pct: -1.96,
      average_rating: 3.8,
      negative_sentiment_pct: 28.5,
      risk_score: 45.8,
      opportunity_score: 42.8,
      priority_tier: "STABLE_PERFORMANCE",
      recommended_action: "Execute dynamic margin repricing & investigate product quality complaints"
    },
    {
      product_id: "7dba7ae3-b564-45d3-b657-23d8cddd229c",
      sku: "SPK002",
      name: "MarketPilot SoundPulse Waterproof Bluetooth Speaker",
      price: 35.69,
      competitor_price: 34.99,
      price_variance_pct: -1.96,
      average_rating: 3.67,
      negative_sentiment_pct: 33.3,
      risk_score: 26.6,
      opportunity_score: 0.0,
      priority_tier: "STABLE_PERFORMANCE",
      recommended_action: "Maintain current pricing & monitor reviews"
    },
    {
      product_id: "2f5e9008-5fa0-4e09-ade4-a21a1770a8b9",
      sku: "WCH003",
      name: "MarketPilot PulseFit Fitness Smartwatch",
      price: 79.99,
      competitor_price: 79.99,
      price_variance_pct: 0.0,
      average_rating: 4.5,
      negative_sentiment_pct: 0.0,
      risk_score: 0.0,
      opportunity_score: 40.0,
      priority_tier: "HIGH_GROWTH_POTENTIAL",
      recommended_action: "Expand marketing campaigns & test premium price tier"
    }
  ],
  competitorPrices: [
    {
      id: "cp-1",
      competitor_name: "SoundWave Pro",
      our_product_sku: "HP001",
      our_product_name: "MarketPilot Studio Over-Ear Wireless Headphones",
      our_price: 53.54,
      competitor_product_name: "SoundWave Elite Over-Ear",
      competitor_price: 52.49,
      currency: "USD",
      difference_pct: -1.96,
      last_updated: new Date().toISOString()
    },
    {
      id: "cp-2",
      competitor_name: "AeroAudio Labs",
      our_product_sku: "HP001",
      our_product_name: "MarketPilot Studio Over-Ear Wireless Headphones",
      our_price: 53.54,
      competitor_product_name: "AeroAudio Horizon ANC",
      competitor_price: 64.99,
      currency: "USD",
      difference_pct: 21.39,
      last_updated: new Date().toISOString()
    },
    {
      id: "cp-3",
      competitor_name: "SoundWave Pro",
      our_product_sku: "SPK002",
      our_product_name: "MarketPilot SoundPulse Waterproof Bluetooth Speaker",
      our_price: 35.69,
      competitor_product_name: "SoundWave AquaBoom Mini",
      competitor_price: 34.99,
      currency: "USD",
      difference_pct: -1.96,
      last_updated: new Date().toISOString()
    }
  ],
  priceAlerts: [
    {
      id: "alert-1",
      product_id: "HP001",
      competitor_name: "SoundWave Pro",
      our_price: 53.54,
      competitor_price: 52.49,
      difference_percentage: -1.96,
      alert_type: "COMPETITOR_LOWER",
      recommendation: "Consider matching to $53.25 to stay competitive while safeguarding 54.8% gross margin floor.",
      status: "ACTIVE",
      created_at: new Date().toISOString()
    }
  ],
  reviews: [
    {
      id: "rev-1",
      product_sku: "HP001",
      rating: 5.0,
      review_text: "Outstanding audio clarity and punchy bass! Extremely comfortable memory foam.",
      sentiment: "positive",
      sentiment_score: 0.85,
      topics: ["sound_audio", "comfort_fit"],
      created_at: new Date().toISOString()
    },
    {
      id: "rev-2",
      product_sku: "HP001",
      rating: 2.0,
      review_text: "Battery life is disappointing. Barely lasts 15 hours on high volume, far below advertised 30.",
      sentiment: "negative",
      sentiment_score: -0.65,
      topics: ["battery"],
      created_at: new Date().toISOString()
    },
    {
      id: "rev-3",
      product_sku: "HP001",
      rating: 1.0,
      review_text: "Disappointed with battery drain. The battery died after 4 months of light use.",
      sentiment: "negative",
      sentiment_score: -0.75,
      topics: ["battery"],
      created_at: new Date().toISOString()
    },
    {
      id: "rev-4",
      product_sku: "SPK002",
      rating: 5.0,
      review_text: "Incredible sound for such a small speaker! Survived a drop in the pool without issue.",
      sentiment: "positive",
      sentiment_score: 0.90,
      topics: ["sound_audio", "build_quality"],
      created_at: new Date().toISOString()
    },
    {
      id: "rev-5",
      product_sku: "WCH003",
      rating: 5.0,
      review_text: "AMOLED screen is crystal clear and battery lasts a full week easily.",
      sentiment: "positive",
      sentiment_score: 0.95,
      topics: ["battery"],
      created_at: new Date().toISOString()
    }
  ],
  reviewsAnalytics: {
    total_reviews: 12,
    average_rating: 4.1,
    sentiment_distribution: { positive: 8, neutral: 1, negative: 3 },
    complaint_breakdown: {
      battery: { count: 3, percentage: 100.0 },
      sound_audio: { count: 1, percentage: 33.3 }
    },
    top_keywords: ["battery", "clarity", "sound", "comfort", "bluetooth", "quality"],
    rating_distribution: { 1: 1, 2: 2, 3: 1, 4: 3, 5: 5 }
  },
  agents: [
    {
      id: "review_analysis",
      name: "Review Analysis Agent",
      role: "Customer Sentiment & Quality Analyst",
      description: "Deterministic TF-IDF extraction, sentiment distribution, and grounded complaint categorization.",
      total_runs: 5,
      last_run_time: new Date().toISOString(),
      last_status: "completed",
      last_summary: "Analyzed 12 customer reviews with 66.7% positive sentiment."
    },
    {
      id: "competitor_price_monitoring",
      name: "Competitor Price Monitoring Agent",
      role: "Pricing Intelligence Strategist",
      description: "Compares real-time competitor prices, triggers alerts on undercut margins, and drafts approval requests.",
      total_runs: 4,
      last_run_time: new Date().toISOString(),
      last_status: "completed",
      last_summary: "Audited 3 competitor price pairings. Created margin alert."
    },
    {
      id: "seo_content_generation",
      name: "SEO Content Generation Agent",
      role: "Verified Product SEO Specialist",
      description: "Generates keyword-optimized product copy, validated against verified attributes to prevent ungrounded claims.",
      total_runs: 3,
      last_run_time: new Date().toISOString(),
      last_status: "completed",
      last_summary: "Generated search-optimized copy for HP001. Claim validation: PASSED."
    },
    {
      id: "marketing_campaign",
      name: "Marketing Campaign Agent",
      role: "Growth Marketing Director",
      description: "Drafts omnichannel social and email campaigns with A/B variations for human editorial sign-off.",
      total_runs: 2,
      last_run_time: new Date().toISOString(),
      last_status: "completed",
      last_summary: "Drafted omnichannel campaign across Social, Ads, and Email."
    },
    {
      id: "business_insights",
      name: "Business Insights Agent",
      role: "Strategic Synthesis Lead",
      description: "Integrates multi-agent intelligence, risk assessments, and executive recommendations requiring approval.",
      total_runs: 6,
      last_run_time: new Date().toISOString(),
      last_status: "completed",
      last_summary: "Synthesized multi-agent operations across sentiment, pricing, and campaign workflows."
    }
  ],
  approvals: [
    {
      id: "appr-1",
      item_type: "PRICE_CHANGE",
      item_id: "HP001",
      title: "Price Adjustment for HP001 Over-Ear Headphones",
      description: "Competitor SoundWave Pro undercut price by 12.5%. Proposed new price: $53.25 (Safe margin: 54.8%)",
      payload: { old_price: 53.54, new_price: 53.25, sku: "HP001" },
      status: "PENDING",
      created_at: new Date().toISOString()
    },
    {
      id: "appr-2",
      item_type: "SEO_CONTENT",
      item_id: "SEO-1",
      title: "SEO Copy for HP001 Wireless Studio Headphones",
      description: "Generated SEO copy. Claim validation passed: True. Pending editorial sign-off.",
      payload: { title: "MarketPilot Wireless Noise-Cancelling Headphones - 30hr Battery" },
      status: "PENDING",
      created_at: new Date().toISOString()
    },
    {
      id: "appr-3",
      item_type: "MARKETING_CAMPAIGN",
      item_id: "CAMP-1",
      title: "Marketing Campaign: Unstoppable Sound Winter Promo",
      description: "Drafted promotional campaign targeting remote workers. Requires marketing director approval.",
      payload: { campaign_name: "Unstoppable Sound - Winter Edition" },
      status: "PENDING",
      created_at: new Date().toISOString()
    }
  ],
  campaigns: [
    {
      id: "camp-1",
      campaign_name: "Unstoppable Sound - Winter Edition",
      campaign_type: "promotional",
      strategy: "Highlight 30-hour battery freedom and fatigue-free comfort to drive holiday conversions.",
      facebook_caption: "30 hours of pure, uninterrupted focus. Meet your new workday essential with comfort that outlasts your longest playlist. 🎧 Shop today and upgrade your sound.",
      instagram_caption: "Zero cords. Zero distractions. Just 30 hours of pure audio bliss. ✨ Tap the link in bio to experience true sound freedom. #AudioLife #WirelessHeadphones",
      ad_copy: "Tired of headphones dying before your day ends? Experience 30 hours of battery life with plush memory foam earcups.",
      email_subject: "Sound that stays with you: Discover 30-hour wireless freedom",
      status: "DRAFT",
      created_at: new Date().toISOString()
    }
  ]
};
