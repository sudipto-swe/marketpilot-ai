import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import { Product } from '../types';
import { FileText, Sparkles, ShieldCheck, ShieldAlert, CheckCircle2 } from 'lucide-react';

export const SEOPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedProductId, setSelectedProductId] = useState<string>('');
  const [lastGenerated, setLastGenerated] = useState<any>(null);

  const { data: products = [] } = useQuery<Product[]>({
    queryKey: ['products'],
    queryFn: async () => {
      const res = await api.get('/products');
      return res.data;
    },
  });

  const generateMutation = useMutation({
    mutationFn: async (productId: string) => {
      const res = await api.post('/seo/generate', { product_id: productId });
      return res.data;
    },
    onSuccess: (data) => {
      setLastGenerated(data);
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
    },
  });

  const selectedProduct = products.find((p) => p.id === selectedProductId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <FileText className="h-6 w-6 text-cyan-400" />
          SEO Content Studio & Grounding Validation
        </h1>
        <p className="text-xs text-slate-400">
          Agent 3 generates search-optimized metadata strictly grounded in verified database specs, preventing unverified guarantees.
        </p>
      </div>

      {/* Product Selector */}
      <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <label className="text-xs font-semibold text-slate-300">Select Target Product Catalog Item</label>
          <select
            value={selectedProductId}
            onChange={(e) => setSelectedProductId(e.target.value)}
            className="w-full sm:w-80 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200"
          >
            <option value="">-- Choose a product --</option>
            {products.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.sku})
              </option>
            ))}
          </select>
        </div>

        <button
          disabled={!selectedProductId || generateMutation.isPending}
          onClick={() => selectedProductId && generateMutation.mutate(selectedProductId)}
          className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-md shadow-cyan-600/30 transition disabled:opacity-50"
        >
          <Sparkles className="h-3.5 w-3.5" />
          {generateMutation.isPending ? 'Generating & Validating Claims...' : 'Generate Grounded SEO Copy'}
        </button>
      </div>

      {/* Ground Truth Specs Preview */}
      {selectedProduct && (
        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-xs space-y-1">
          <span className="font-semibold text-slate-400 uppercase tracking-wider text-[10px]">Verified Ground-Truth Attributes:</span>
          <p className="font-mono text-cyan-400">{JSON.stringify(selectedProduct.attributes || {})}</p>
        </div>
      )}

      {/* Results View */}
      {lastGenerated && (
        <div className="space-y-6">
          {/* Claim Validation Status Banner */}
          <div className={`p-4 rounded-xl border flex items-center justify-between ${
            lastGenerated.content?.is_claim_validated
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
              : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
          }`}>
            <div className="flex items-center gap-2">
              {lastGenerated.content?.is_claim_validated ? (
                <ShieldCheck className="h-5 w-5" />
              ) : (
                <ShieldAlert className="h-5 w-5" />
              )}
              <div>
                <p className="text-xs font-bold">
                  {lastGenerated.content?.is_claim_validated
                    ? 'Claim Validation Passed — Grounded in Verified Attributes'
                    : 'Claim Validation Detected Potential Discrepancies'}
                </p>
                <p className="text-[11px] text-slate-400">
                  Confidence Score: {(lastGenerated.confidence * 100).toFixed(0)}% • Draft submitted to Human Approval Center.
                </p>
              </div>
            </div>
            <span className="text-[10px] font-mono px-2 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300">
              PENDING_APPROVAL
            </span>
          </div>

          {/* Generated Fields */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
              <div>
                <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">SEO Optimized Title</label>
                <p className="text-sm font-bold text-white mt-1 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                  {lastGenerated.content?.generated_title}
                </p>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Product Meta Description</label>
                <p className="text-xs text-slate-300 mt-1 bg-slate-950 p-2.5 rounded-lg border border-slate-800 leading-relaxed">
                  {lastGenerated.content?.meta_description || lastGenerated.content?.generated_description}
                </p>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Alt Text For Media</label>
                <p className="text-xs text-slate-300 mt-1 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                  {lastGenerated.content?.alt_text}
                </p>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
              <div>
                <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Feature Bullet Points</label>
                <ul className="mt-1 space-y-1.5 text-xs text-slate-300 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                  {lastGenerated.content?.bullet_points?.map((bp: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-cyan-400">•</span> {bp}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">High-Intent Keywords</label>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {lastGenerated.content?.keywords?.map((kw: string) => (
                    <span key={kw} className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-xs font-mono">
                      #{kw}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
