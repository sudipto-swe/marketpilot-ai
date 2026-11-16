import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import type { CompetitorPrice, PriceAlert } from '../types';
import { TrendingDown, AlertTriangle, Upload, Sparkles, ShieldCheck, DollarSign, Calculator } from 'lucide-react';

export const CompetitorsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [activeRepriceSku, setActiveRepriceSku] = useState<string | null>('HP001');

  const { data: prices = [], isLoading: isPricesLoading } = useQuery<CompetitorPrice[]>({
    queryKey: ['competitor-prices'],
    queryFn: async () => {
      const res = await api.get('/competitors/prices');
      return res.data;
    },
  });

  const { data: alerts = [] } = useQuery<PriceAlert[]>({
    queryKey: ['price-alerts'],
    queryFn: async () => {
      const res = await api.get('/competitors/alerts');
      return res.data;
    },
  });

  const { data: dynamicRepricing } = useQuery({
    queryKey: ['dynamic-repricing', activeRepriceSku],
    queryFn: async () => {
      if (!activeRepriceSku) return null;
      const res = await api.get(`/competitors/dynamic-repricing/${activeRepriceSku}`);
      return res.data;
    },
    enabled: !!activeRepriceSku,
  });

  const runPriceAgentMutation = useMutation({
    mutationFn: async () => {
      return api.post('/agents/competitor_price_monitoring/run');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitor-prices'] });
      queryClient.invalidateQueries({ queryKey: ['price-alerts'] });
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      alert('Competitor Price Monitoring Agent executed! Created alerts and approval drafts.');
    },
  });

  const importMutation = useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append('file', file);
      return api.post('/competitors/import', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitor-prices'] });
      setIsImportModalOpen(false);
      setSelectedFile(null);
    },
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <TrendingDown className="h-6 w-6 text-rose-400" />
            Competitor Intelligence & Margin Guardrail Engine
          </h1>
          <p className="text-xs text-slate-400">
            Real-time price comparisons, automated margin undercut alerts, and dynamic profit-protected repricing algorithms.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsImportModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
          >
            <Upload className="h-3.5 w-3.5" /> Import Competitor CSV
          </button>
          <button
            onClick={() => runPriceAgentMutation.mutate()}
            disabled={runPriceAgentMutation.isPending}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-md shadow-rose-600/30 transition disabled:opacity-50"
          >
            <Sparkles className="h-3.5 w-3.5" />
            {runPriceAgentMutation.isPending ? 'Agent Auditing...' : 'Run Price Agent'}
          </button>
        </div>
      </div>

      {/* Dynamic Margin Guardrail Simulation Panel */}
      {dynamicRepricing && (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-indigo-500/30 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-emerald-400" />
              <h2 className="text-sm font-bold text-white">
                Intelligent Dynamic Repricing Model (SKU: {activeRepriceSku})
              </h2>
            </div>
            <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              {dynamicRepricing.guardrail_status}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400">Our Current Price</span>
              <p className="text-base font-bold text-slate-100">${dynamicRepricing.current_price?.toFixed(2)}</p>
              <span className="text-[10px] text-slate-500">Margin: {dynamicRepricing.current_margin_pct}%</span>
            </div>

            <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400">Competitor Price</span>
              <p className="text-base font-bold text-rose-400">${dynamicRepricing.competitor_price?.toFixed(2)}</p>
              <span className="text-[10px] text-slate-500">Market benchmark</span>
            </div>

            <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400">Unit Cost (COGS) Floor</span>
              <p className="text-base font-bold text-amber-400">${dynamicRepricing.unit_cost?.toFixed(2)}</p>
              <span className="text-[10px] text-slate-500">Min safe: ${dynamicRepricing.min_allowable_price?.toFixed(2)}</span>
            </div>

            <div className="p-3 bg-slate-950/80 rounded-xl border border-indigo-500/40 bg-indigo-950/20">
              <span className="text-[10px] text-indigo-300 font-semibold">AI Recommended Price</span>
              <p className="text-base font-bold text-emerald-400">${dynamicRepricing.recommended_price?.toFixed(2)}</p>
              <span className="text-[10px] text-emerald-300">Target Margin: {dynamicRepricing.projected_margin_pct}%</span>
            </div>
          </div>
        </div>
      )}

      {/* Active Alerts Cards */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-white flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-rose-400" />
          Active Price Movement Alerts ({alerts.length})
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {alerts.length === 0 ? (
            <p className="text-xs text-slate-400 col-span-2">No active price alerts. Run the Price Agent to scan competitors.</p>
          ) : (
            alerts.map((alert) => (
              <div key={alert.id} className="p-4 rounded-xl bg-slate-900 border border-rose-500/30 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-white">{alert.competitor_name}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                    {alert.difference_percentage}% Difference
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs text-slate-300">
                  <span>Our Price: <strong className="text-white">${alert.our_price.toFixed(2)}</strong></span>
                  <span>Competitor: <strong className="text-rose-400">${alert.competitor_price.toFixed(2)}</strong></span>
                </div>
                <p className="text-[11px] text-slate-400 bg-slate-950 p-2 rounded-lg border border-slate-800">
                  💡 {alert.recommendation}
                </p>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Competitor Price Comparison Table */}
      <div className="rounded-2xl bg-slate-900/80 border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950/60 text-slate-400 uppercase tracking-wider border-b border-slate-800">
            <tr>
              <th className="py-3.5 px-4">Our Product</th>
              <th className="py-3.5 px-4">SKU</th>
              <th className="py-3.5 px-4">Our Price</th>
              <th className="py-3.5 px-4">Competitor</th>
              <th className="py-3.5 px-4">Competitor Product</th>
              <th className="py-3.5 px-4">Competitor Price</th>
              <th className="py-3.5 px-4">Variance</th>
              <th className="py-3.5 px-4 text-right">Repricing Sim</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {isPricesLoading ? (
              <tr>
                <td colSpan={8} className="text-center py-8 text-slate-400">Loading price tracking...</td>
              </tr>
            ) : prices.length === 0 ? (
              <tr>
                <td colSpan={8} className="text-center py-8 text-slate-400">No competitor prices tracked. Import competitor CSV.</td>
              </tr>
            ) : (
              prices.map((item) => (
                <tr key={item.id} className="hover:bg-slate-800/30 transition">
                  <td className="py-3.5 px-4 font-medium text-white">{item.our_product_name}</td>
                  <td className="py-3.5 px-4 font-mono text-indigo-400">{item.our_product_sku}</td>
                  <td className="py-3.5 px-4 font-bold text-slate-100">${item.our_price.toFixed(2)}</td>
                  <td className="py-3.5 px-4 text-slate-300">{item.competitor_name}</td>
                  <td className="py-3.5 px-4 text-slate-400">{item.competitor_product_name}</td>
                  <td className="py-3.5 px-4 font-bold text-slate-200">${item.competitor_price.toFixed(2)}</td>
                  <td className="py-3.5 px-4">
                    <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                      item.difference_pct < 0
                        ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    }`}>
                      {item.difference_pct > 0 ? `+${item.difference_pct}%` : `${item.difference_pct}%`}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => setActiveRepriceSku(item.our_product_sku)}
                      className="px-2.5 py-1 rounded-md bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 border border-indigo-500/20 text-[11px] font-semibold transition"
                    >
                      Simulate
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* CSV Import Modal */}
      {isImportModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4">
            <h2 className="text-base font-bold text-white">Import Competitor Prices CSV</h2>
            <p className="text-xs text-slate-400">
              CSV must have headers: <code className="text-cyan-400">competitor_name, product_sku, competitor_product_name, price, currency, recorded_at, source</code>
            </p>
            <input
              type="file"
              accept=".csv"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              className="w-full text-xs text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-rose-600 file:text-white hover:file:bg-rose-500 cursor-pointer"
            />
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setIsImportModalOpen(false)}
                className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={!selectedFile || importMutation.isPending}
                onClick={() => selectedFile && importMutation.mutate(selectedFile)}
                className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold disabled:opacity-50"
              >
                {importMutation.isPending ? 'Importing...' : 'Upload & Match Prices'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
