import React from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import type { DashboardStats } from '../types';
import {
  Package,
  MessageSquare,
  TrendingDown,
  CheckCircle2,
  Sparkles,
  Star,
  Target,
  ShieldCheck,
  AlertOctagon
} from 'lucide-react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip
} from 'recharts';

export const DashboardPage: React.FC = () => {
  const { data: stats, isLoading, refetch } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const res = await api.get('/insights/stats');
      return res.data;
    },
  });

  const { data: matrix = [] } = useQuery<any[]>({
    queryKey: ['opportunity-matrix'],
    queryFn: async () => {
      const res = await api.get('/insights/opportunity-matrix');
      return res.data;
    },
  });

  const sentimentData = [
    { name: 'Positive', value: stats?.positive_sentiment_percentage || 0, color: '#10b981' },
    { name: 'Negative', value: stats?.negative_sentiment_percentage || 0, color: '#f43f5e' },
    { name: 'Neutral', value: Math.max(0, 100 - (stats?.positive_sentiment_percentage || 0) - (stats?.negative_sentiment_percentage || 0)), color: '#64748b' },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-2">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent" />
          <p className="text-sm text-slate-400">Loading live executive telemetry...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-indigo-950/60 via-slate-900 to-slate-900 border border-indigo-500/20 shadow-xl">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Executive Operations Cockpit
          </h1>
          <p className="text-sm text-slate-400">
            Real-time telemetry across products, customer reviews, competitor pricing movements, and AI approval queues.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => refetch()}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            Refresh Data
          </button>
        </div>
      </div>

      {/* KPI Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Products */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs font-medium text-slate-400">Active Products</p>
            <p className="text-2xl font-bold text-white">{stats?.total_products || 0}</p>
            <p className="text-[11px] text-slate-400">Tracked inventory units</p>
          </div>
          <div className="h-10 w-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Package className="h-5 w-5" />
          </div>
        </div>

        {/* Reviews & Rating */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs font-medium text-slate-400">Reviews / Avg Rating</p>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-white">{stats?.total_reviews || 0}</span>
              <span className="flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                {stats?.average_rating || 0}
              </span>
            </div>
            <p className="text-[11px] text-slate-400">{stats?.positive_sentiment_percentage || 0}% positive sentiment</p>
          </div>
          <div className="h-10 w-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <MessageSquare className="h-5 w-5" />
          </div>
        </div>

        {/* Competitor Price Alerts */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs font-medium text-slate-400">Price Alerts</p>
            <p className="text-2xl font-bold text-rose-400">{stats?.active_price_alerts || 0}</p>
            <p className="text-[11px] text-slate-400">Undercut margin risks</p>
          </div>
          <div className="h-10 w-10 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
            <TrendingDown className="h-5 w-5" />
          </div>
        </div>

        {/* Pending Approvals */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs font-medium text-slate-400">Pending Approvals</p>
            <p className="text-2xl font-bold text-cyan-400">{stats?.pending_approvals || 0}</p>
            <p className="text-[11px] text-slate-400">Human-in-the-loop decisions</p>
          </div>
          <div className="h-10 w-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <CheckCircle2 className="h-5 w-5" />
          </div>
        </div>
      </div>

      {/* Strategic Opportunity & Risk Matrix (Enterprise Feature beating Gumloop/Alhena) */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Target className="h-5 w-5 text-indigo-400" />
              Strategic Opportunity & Risk Matrix
            </h2>
            <p className="text-xs text-slate-400">
              Cross-analyzes real competitor price gaps, negative customer sentiment, and rating momentum into actionable priority tiers.
            </p>
          </div>
          <span className="text-[10px] font-mono px-2.5 py-1 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            Automated Synthesis
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {matrix.map((item) => (
            <div
              key={item.sku}
              className={`p-4 rounded-xl border flex flex-col justify-between space-y-3 ${
                item.priority_tier === 'CRITICAL_ACTION_REQUIRED'
                  ? 'bg-rose-950/20 border-rose-500/30'
                  : item.priority_tier === 'HIGH_GROWTH_POTENTIAL'
                  ? 'bg-emerald-950/20 border-emerald-500/30'
                  : 'bg-slate-950/60 border-slate-800'
              }`}
            >
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-indigo-400">{item.sku}</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    item.priority_tier === 'CRITICAL_ACTION_REQUIRED'
                      ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                      : item.priority_tier === 'HIGH_GROWTH_POTENTIAL'
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-slate-800 text-slate-300'
                  }`}>
                    {item.priority_tier.replace(/_/g, ' ')}
                  </span>
                </div>
                <h3 className="text-xs font-bold text-white truncate">{item.name}</h3>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
                <div>
                  <span>Price Gap: </span>
                  <strong className={item.price_variance_pct < 0 ? 'text-rose-400' : 'text-emerald-400'}>
                    {item.price_variance_pct}%
                  </strong>
                </div>
                <div>
                  <span>Avg Rating: </span>
                  <strong className="text-amber-400">{item.average_rating} ★</strong>
                </div>
                <div>
                  <span>Risk Score: </span>
                  <strong className="text-slate-200">{item.risk_score} / 100</strong>
                </div>
                <div>
                  <span>Opportunity: </span>
                  <strong className="text-slate-200">{item.opportunity_score} / 100</strong>
                </div>
              </div>

              <p className="text-[11px] text-slate-300 leading-relaxed italic">
                👉 {item.recommended_action}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Grid: Charts & Synthesis */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sentiment Analysis Visualizer */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            Deterministic Sentiment Distribution
          </h2>
          <p className="text-xs text-slate-400">Computed via Scikit-learn TF-IDF & NLP scoring engine.</p>
          <div className="h-48 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-around text-xs">
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
              <span className="text-slate-300">Positive ({stats?.positive_sentiment_percentage}%)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-rose-500" />
              <span className="text-slate-300">Negative ({stats?.negative_sentiment_percentage}%)</span>
            </div>
          </div>
        </div>

        {/* Latest Business Insights Synthesis */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-indigo-400" />
                Latest Business Insights & Synthesis
              </h2>
              <span className="text-[11px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 font-medium">
                Agent 5 Output
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              {stats?.latest_business_insights?.summary}
            </p>
          </div>

          <div className="space-y-2">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Prioritized Action Recommendations
            </h3>
            <div className="space-y-2">
              {stats?.latest_business_insights?.recommendations?.length ? (
                stats.latest_business_insights.recommendations.map((rec: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60 flex items-start justify-between text-xs"
                  >
                    <div className="space-y-1">
                      <p className="font-medium text-slate-200">{rec.action || rec.recommendation}</p>
                      {rec.rationale && <p className="text-slate-400 text-[11px]">{rec.rationale}</p>}
                    </div>
                    {rec.requires_approval && (
                      <span className="shrink-0 ml-3 text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        Needs Approval
                      </span>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-400">Run the Business Insights Agent to populate verified actions.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Agent Executions List */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
        <h2 className="text-base font-semibold text-white">Recent Multi-Agent Executions</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/60 text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Agent Name</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Summary</th>
                <th className="py-3 px-4">Executed At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {stats?.recent_agent_runs?.map((run) => (
                <tr key={run.id} className="hover:bg-slate-800/30 transition">
                  <td className="py-3 px-4 font-medium text-white capitalize">
                    {run.agent_name.replace(/_/g, ' ')}
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {run.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 max-w-md truncate text-slate-400">{run.summary}</td>
                  <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                    {new Date(run.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
