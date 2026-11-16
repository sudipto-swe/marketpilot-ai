import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import { Review } from '../types';
import { MessageSquare, Upload, Star, Play, Sparkles } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

export const ReviewsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);

  const { data: reviews = [], isLoading: isReviewsLoading } = useQuery<Review[]>({
    queryKey: ['reviews'],
    queryFn: async () => {
      const res = await api.get('/reviews');
      return res.data;
    },
  });

  const { data: analytics } = useQuery({
    queryKey: ['reviews-analytics'],
    queryFn: async () => {
      const res = await api.get('/reviews/analytics');
      return res.data;
    },
  });

  const runAgentMutation = useMutation({
    mutationFn: async () => {
      return api.post('/agents/review_analysis/run');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] });
      queryClient.invalidateQueries({ queryKey: ['reviews-analytics'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      alert('Review Analysis Agent completed successfully!');
    },
  });

  const importMutation = useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append('file', file);
      return api.post('/reviews/import', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] });
      queryClient.invalidateQueries({ queryKey: ['reviews-analytics'] });
      setIsImportModalOpen(false);
      setSelectedFile(null);
    },
  });

  const ratingChartData = analytics?.rating_distribution
    ? Object.entries(analytics.rating_distribution).map(([star, count]) => ({
        rating: `${star} Star`,
        count,
      }))
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <MessageSquare className="h-6 w-6 text-emerald-400" />
            Customer Review Intelligence & Deterministic NLP
          </h1>
          <p className="text-xs text-slate-400">
            Computed sentiment baselines, TF-IDF topic extractions, and grounding evidence for Agent 1.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsImportModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
          >
            <Upload className="h-3.5 w-3.5" /> Import Reviews CSV
          </button>
          <button
            onClick={() => runAgentMutation.mutate()}
            disabled={runAgentMutation.isPending}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/30 transition disabled:opacity-50"
          >
            <Sparkles className="h-3.5 w-3.5" />
            {runAgentMutation.isPending ? 'Agent Running...' : 'Execute Review Agent'}
          </button>
        </div>
      </div>

      {/* Analytics Summary Panels */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Rating Breakdown Chart */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
          <h3 className="text-sm font-semibold text-white">Rating Distribution</h3>
          <div className="h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ratingChartData}>
                <XAxis dataKey="rating" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip />
                <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Complaint Breakdown */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
          <h3 className="text-sm font-semibold text-white">Repeated Complaint Topics</h3>
          <p className="text-[11px] text-slate-400">Exact percentage of negative review mentions.</p>
          <div className="space-y-2">
            {analytics?.complaint_breakdown && Object.keys(analytics.complaint_breakdown).length > 0 ? (
              Object.entries(analytics.complaint_breakdown).map(([topic, data]: [string, any]) => (
                <div key={topic} className="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-950/60 border border-slate-800">
                  <span className="font-medium capitalize text-slate-300">{topic.replace('_', ' ')}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-rose-400 font-bold">{data.percentage}%</span>
                    <span className="text-[10px] text-slate-500">({data.count} mentions)</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400">No negative complaints detected in corpus.</p>
            )}
          </div>
        </div>

        {/* TF-IDF Top Keywords */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
          <h3 className="text-sm font-semibold text-white">TF-IDF Extracted Terms</h3>
          <p className="text-[11px] text-slate-400">Deterministic key phrases extracted from reviews.</p>
          <div className="flex flex-wrap gap-1.5">
            {analytics?.top_keywords?.map((kw: string) => (
              <span key={kw} className="px-2.5 py-1 rounded-md bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-xs font-mono">
                #{kw}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Review Records Table */}
      <div className="rounded-2xl bg-slate-900/80 border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950/60 text-slate-400 uppercase tracking-wider border-b border-slate-800">
            <tr>
              <th className="py-3.5 px-4">Product SKU</th>
              <th className="py-3.5 px-4">Rating</th>
              <th className="py-3.5 px-4">Sentiment</th>
              <th className="py-3.5 px-4">Detected Topics</th>
              <th className="py-3.5 px-4">Review Text</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {isReviewsLoading ? (
              <tr>
                <td colSpan={5} className="text-center py-8 text-slate-400">Loading customer reviews...</td>
              </tr>
            ) : reviews.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center py-8 text-slate-400">No customer reviews present. Import reviews CSV.</td>
              </tr>
            ) : (
              reviews.map((r) => (
                <tr key={r.id} className="hover:bg-slate-800/30 transition">
                  <td className="py-3.5 px-4 font-mono font-bold text-indigo-400">{r.product_sku}</td>
                  <td className="py-3.5 px-4">
                    <span className="flex items-center gap-1 font-semibold text-amber-400">
                      <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                      {r.rating.toFixed(1)}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      r.sentiment === 'positive'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : r.sentiment === 'negative'
                        ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                    }`}>
                      {r.sentiment || 'neutral'}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="flex gap-1 flex-wrap">
                      {r.topics?.map((t) => (
                        <span key={t} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">
                          {t}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-3.5 px-4 max-w-md text-slate-300 italic">"{r.review_text}"</td>
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
            <h2 className="text-base font-bold text-white">Import Customer Reviews CSV</h2>
            <p className="text-xs text-slate-400">
              CSV must have headers: <code className="text-cyan-400">review_id, product_sku, rating, review_text, review_date, source</code>
            </p>
            <input
              type="file"
              accept=".csv"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              className="w-full text-xs text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-emerald-600 file:text-white hover:file:bg-emerald-500 cursor-pointer"
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
                className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold disabled:opacity-50"
              >
                {importMutation.isPending ? 'Importing...' : 'Upload & Process Reviews'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
