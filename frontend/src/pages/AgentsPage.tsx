import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import type { AgentMeta, Product } from '../types';
import { Bot, Play, Layers, CheckCircle2, Clock } from 'lucide-react';

export const AgentsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedProductId, setSelectedProductId] = useState<string>('');
  const [activeFeedback, setActiveFeedback] = useState<string | null>(null);

  const { data: products = [] } = useQuery<Product[]>({
    queryKey: ['products'],
    queryFn: async () => {
      const res = await api.get('/products');
      return res.data;
    },
  });

  const { data: agents = [] } = useQuery<AgentMeta[]>({
    queryKey: ['agents'],
    queryFn: async () => {
      const res = await api.get('/agents');
      return res.data;
    },
  });

  const runIndividualMutation = useMutation({
    mutationFn: async (agentId: string) => {
      const params: any = {};
      if (selectedProductId) {
        params.product_id = selectedProductId;
      }
      return api.post(`/agents/${agentId}/run`, {}, { params });
    },
    onSuccess: (_res, agentId) => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
      queryClient.invalidateQueries({ queryKey: ['price-alerts'] });
      setActiveFeedback(`Agent '${agentId}' successfully executed!`);
      setTimeout(() => setActiveFeedback(null), 4000);
    },
    onError: (err: any) => {
      setActiveFeedback(`Execution error: ${err.response?.data?.detail || err.message}`);
      setTimeout(() => setActiveFeedback(null), 5000);
    }
  });

  const runFullWorkflowMutation = useMutation({
    mutationFn: async () => {
      const params: any = {};
      if (selectedProductId) {
        params.product_id = selectedProductId;
      }
      return api.post('/agents/orchestrate/full', {}, { params });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
      queryClient.invalidateQueries({ queryKey: ['price-alerts'] });
      setActiveFeedback('Full 5-Agent Autonomous Multi-Agent Workflow executed successfully!');
      setTimeout(() => setActiveFeedback(null), 4000);
    },
  });

  return (
    <div className="space-y-6">
      {/* Toast Feedback */}
      {activeFeedback && (
        <div className="p-3.5 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs flex items-center justify-between">
          <span>{activeFeedback}</span>
          <button onClick={() => setActiveFeedback(null)} className="text-[10px] underline">Dismiss</button>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Bot className="h-6 w-6 text-indigo-400" />
            AI Multi-Agent Control Center
          </h1>
          <p className="text-xs text-slate-400">
            Monitor, inspect execution telemetry, and trigger individual or coordinated multi-agent workflows.
          </p>
        </div>
        <button
          onClick={() => runFullWorkflowMutation.mutate()}
          disabled={runFullWorkflowMutation.isPending}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
        >
          <Layers className="h-4 w-4" />
          {runFullWorkflowMutation.isPending ? 'Orchestrating 5 Agents...' : 'Run Full Multi-Agent Workflow'}
        </button>
      </div>

      {/* Target Product Scope Selector */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-300">Target Product Scope:</span>
          <select
            value={selectedProductId}
            onChange={(e) => setSelectedProductId(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
          >
            <option value="">Auto-resolve from inventory</option>
            {products.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.sku})
              </option>
            ))}
          </select>
        </div>
        <span className="text-slate-400 text-[11px]">
          Runs will automatically contextualize findings, specs, and reviews for the chosen product.
        </span>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between space-y-4 shadow-sm hover:border-slate-700 transition"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                  {agent.id}
                </span>
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400">
                  <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
                  {agent.last_status}
                </span>
              </div>
              <h2 className="text-base font-bold text-white">{agent.name}</h2>
              <p className="text-xs text-indigo-400 font-medium">{agent.role}</p>
              <p className="text-xs text-slate-400 leading-relaxed">{agent.description}</p>
            </div>

            <div className="space-y-3 pt-3 border-t border-slate-800/80">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Total Executions:</span>
                <strong className="text-white font-mono">{agent.total_runs}</strong>
              </div>
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Last Run:</span>
                <span className="text-[11px] font-mono text-slate-300">
                  {agent.last_run_time ? new Date(agent.last_run_time).toLocaleTimeString() : 'Never'}
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-[11px] text-slate-400 truncate">
                {agent.last_summary}
              </div>

              <button
                disabled={runIndividualMutation.isPending}
                onClick={() => runIndividualMutation.mutate(agent.id)}
                className="w-full flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition disabled:opacity-50"
              >
                <Play className="h-3.5 w-3.5 text-indigo-400" />
                {runIndividualMutation.isPending && runIndividualMutation.variables === agent.id
                  ? 'Executing Agent...'
                  : 'Run Agent Individually'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
