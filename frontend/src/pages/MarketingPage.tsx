import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import { Product } from '../types';
import { Megaphone, Sparkles, Send, Copy, Check } from 'lucide-react';

export const MarketingPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [campaignName, setCampaignName] = useState('Holiday Audio Flash Sale');
  const [campaignType, setCampaignType] = useState('promotional');
  const [selectedProductId, setSelectedProductId] = useState('');
  const [targetAudience, setTargetAudience] = useState('Commuters, remote workers, audio enthusiasts');
  const [generatedDraft, setGeneratedDraft] = useState<any>(null);

  const { data: products = [] } = useQuery<Product[]>({
    queryKey: ['products'],
    queryFn: async () => {
      const res = await api.get('/products');
      return res.data;
    },
  });

  const { data: campaigns = [] } = useQuery({
    queryKey: ['campaigns'],
    queryFn: async () => {
      const res = await api.get('/marketing/campaigns');
      return res.data;
    },
  });

  const generateMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post('/marketing/generate', {
        campaign_name: campaignName,
        campaign_type: campaignType,
        product_id: selectedProductId || null,
        target_audience: targetAudience,
      });
      return res.data;
    },
    onSuccess: (data) => {
      setGeneratedDraft(data);
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
    },
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <Megaphone className="h-6 w-6 text-fuchsia-400" />
          Marketing Campaign Studio & Variations
        </h1>
        <p className="text-xs text-slate-400">
          Agent 4 generates omnichannel copy drafts and A/B variations. All outputs remain drafts until human approval.
        </p>
      </div>

      {/* Creation Config Card */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
        <h2 className="text-sm font-bold text-white">Draft New Omnichannel Campaign</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div>
            <label className="block text-slate-400 mb-1">Campaign Name</label>
            <input
              type="text"
              value={campaignName}
              onChange={(e) => setCampaignName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200"
            />
          </div>
          <div>
            <label className="block text-slate-400 mb-1">Campaign Type</label>
            <select
              value={campaignType}
              onChange={(e) => setCampaignType(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200"
            >
              <option value="promotional">Promotional</option>
              <option value="seasonal">Seasonal</option>
              <option value="product_launch">Product Launch</option>
              <option value="retargeting">Retargeting</option>
            </select>
          </div>
          <div>
            <label className="block text-slate-400 mb-1">Focus Product (Optional)</label>
            <select
              value={selectedProductId}
              onChange={(e) => setSelectedProductId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200"
            >
              <option value="">Store-wide Catalog</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-slate-400 mb-1">Target Audience</label>
            <input
              type="text"
              value={targetAudience}
              onChange={(e) => setTargetAudience(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200"
            />
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            disabled={generateMutation.isPending}
            onClick={() => generateMutation.mutate()}
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg bg-fuchsia-600 hover:bg-fuchsia-500 text-white text-xs font-semibold shadow-md shadow-fuchsia-600/30 transition disabled:opacity-50"
          >
            <Sparkles className="h-3.5 w-3.5" />
            {generateMutation.isPending ? 'Drafting Omnichannel Copy...' : 'Generate Campaign Drafts'}
          </button>
        </div>
      </div>

      {/* Generated Campaigns List */}
      <div className="space-y-4">
        <h2 className="text-sm font-semibold text-white">Campaign History & Editorial Drafts</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {campaigns.length === 0 ? (
            <p className="text-xs text-slate-400 col-span-2">No campaigns drafted yet.</p>
          ) : (
            campaigns.map((camp: any) => (
              <div key={camp.id} className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-white">{camp.campaign_name}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                    {camp.status}
                  </span>
                </div>
                <div className="text-xs text-slate-400">
                  <p><strong>Strategy:</strong> {camp.strategy}</p>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1 text-xs">
                  <span className="text-[10px] uppercase font-bold text-fuchsia-400">Social Caption:</span>
                  <p className="text-slate-300 italic">{camp.instagram_caption || camp.facebook_caption}</p>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1 text-xs">
                  <span className="text-[10px] uppercase font-bold text-indigo-400">Email Subject:</span>
                  <p className="text-slate-300">{camp.email_subject}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
