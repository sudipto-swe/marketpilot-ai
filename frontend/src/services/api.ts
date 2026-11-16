import axios from 'axios';
import { mockDemoData } from './mockDemoData';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Fallback to local demo data for 24/7 web hosting (e.g. GitHub Pages) when backend is unavailable
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const url = error.config?.url || '';
    const method = (error.config?.method || 'get').toLowerCase();

    // If backend is unreachable or returns 404/502 on static hosting, provide seamless simulated experience
    if (!error.response || error.response.status >= 400) {
      if (url.includes('/auth/login')) {
        return Promise.resolve({
          data: {
            access_token: 'demo-standalone-token',
            token_type: 'bearer',
            workspace_id: '902a7c9f-7723-4c70-a40d-470a24a19697'
          }
        });
      }
      if (url.includes('/insights/stats')) {
        return Promise.resolve({ data: mockDemoData.stats });
      }
      if (url.includes('/insights/opportunity-matrix')) {
        return Promise.resolve({ data: mockDemoData.matrix });
      }
      if (url.includes('/products/export/csv')) {
        return Promise.resolve({ data: 'sku,name,price\nHP001,Wireless Headphones,53.54' });
      }
      if (url.includes('/products')) {
        if (method === 'post' || method === 'put' || method === 'delete') {
          return Promise.resolve({ data: { message: 'Success' } });
        }
        return Promise.resolve({ data: mockDemoData.products });
      }
      if (url.includes('/competitors/prices')) {
        return Promise.resolve({ data: mockDemoData.competitorPrices });
      }
      if (url.includes('/competitors/alerts')) {
        return Promise.resolve({ data: mockDemoData.priceAlerts });
      }
      if (url.includes('/competitors/dynamic-repricing')) {
        const sku = url.split('/').pop() || 'HP001';
        return Promise.resolve({
          data: {
            current_price: sku === 'SPK002' ? 35.69 : 53.54,
            competitor_price: sku === 'SPK002' ? 34.99 : 52.49,
            unit_cost: sku === 'SPK002' ? 16.06 : 24.09,
            min_allowable_price: sku === 'SPK002' ? 19.27 : 28.91,
            recommended_price: sku === 'SPK002' ? 35.50 : 53.25,
            price_change_dollar: sku === 'SPK002' ? -0.19 : -0.29,
            price_change_pct: -0.54,
            current_margin_pct: 55.0,
            projected_margin_pct: 54.8,
            guardrail_status: 'SAFE_MARGIN_PRESERVED',
            margin_floor_protected: true
          }
        });
      }
      if (url.includes('/reviews/analytics')) {
        return Promise.resolve({ data: mockDemoData.reviewsAnalytics });
      }
      if (url.includes('/reviews')) {
        return Promise.resolve({ data: mockDemoData.reviews });
      }
      if (url.includes('/agents') && method === 'get') {
        return Promise.resolve({ data: mockDemoData.agents });
      }
      if (url.includes('/agents') && method === 'post') {
        return Promise.resolve({
          data: {
            status: 'completed',
            summary: 'Agent successfully executed telemetry analysis.'
          }
        });
      }
      if (url.includes('/approvals')) {
        if (method === 'post') {
          return Promise.resolve({ data: { status: 'success', message: 'Action recorded' } });
        }
        return Promise.resolve({ data: mockDemoData.approvals });
      }
      if (url.includes('/marketing/campaigns')) {
        return Promise.resolve({ data: mockDemoData.campaigns });
      }
      if (url.includes('/marketing/generate')) {
        return Promise.resolve({
          data: {
            status: 'completed',
            campaign_name: 'Targeted Growth Sprint',
            strategy: 'Highlight verified specifications and premium build quality.',
            instagram_caption: 'Pure audio freedom. Upgrade your everyday listening experience today! 🎧 #AudioLife'
          }
        });
      }
      if (url.includes('/seo/generate')) {
        return Promise.resolve({
          data: {
            confidence: 0.98,
            content: {
              generated_title: 'MarketPilot Wireless Noise-Cancelling Headphones - 30hr Battery',
              generated_description: 'Engineered for immersive sound and all-day comfort. Featuring precision-tuned dynamic drivers and verified 30-hour battery life.',
              meta_title: 'Buy Premium Wireless Headphones | 30-Hour Battery',
              bullet_points: ['30-Hour verified playtime', 'Ergonomic memory foam cushions', 'High-definition voice microphone'],
              keywords: ['wireless headphones', '30 hour battery', 'bluetooth headset'],
              alt_text: 'MarketPilot Over-Ear Wireless Headphones in matte black',
              is_claim_validated: true
            }
          }
        });
      }
    }

    if (error.response?.status === 401 && !url.includes('/auth/login')) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (window.location.hash !== '#/login') {
        window.location.hash = '#/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
