import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import { ApprovalItem } from '../types';
import { CheckCircle2, XCircle, Clock, ShieldCheck } from 'lucide-react';

export const ApprovalsPage: React.FC = () => {
  const queryClient = useQueryClient();

  const { data: approvals = [], isLoading } = useQuery<ApprovalItem[]>({
    queryKey: ['approvals'],
    queryFn: async () => {
      const res = await api.get('/approvals');
      return res.data;
    },
  });

  const approveMutation = useMutation({
    mutationFn: async (id: string) => {
      return api.post(`/approvals/${id}/approve`, { notes: 'Approved via Human Approval Center' });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: async (id: string) => {
      return api.post(`/approvals/${id}/reject`, { notes: 'Rejected by human operator' });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
    },
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <ShieldCheck className="h-6 w-6 text-cyan-400" />
          Human Approval Center (Human-In-The-Loop)
        </h1>
        <p className="text-xs text-slate-400">
          Strict guardrail: AI agents cannot change prices or publish marketing content without explicit human review and authorization.
        </p>
      </div>

      {/* Approvals Table */}
      <div className="rounded-2xl bg-slate-900/80 border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950/60 text-slate-400 uppercase tracking-wider border-b border-slate-800">
            <tr>
              <th className="py-3.5 px-4">Type</th>
              <th className="py-3.5 px-4">Title & Description</th>
              <th className="py-3.5 px-4">Payload Details</th>
              <th className="py-3.5 px-4">Status</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {isLoading ? (
              <tr>
                <td colSpan={5} className="text-center py-8 text-slate-400">Loading pending requests...</td>
              </tr>
            ) : approvals.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center py-8 text-slate-400">No approval requests currently pending.</td>
              </tr>
            ) : (
              approvals.map((item) => (
                <tr key={item.id} className="hover:bg-slate-800/30 transition">
                  <td className="py-3.5 px-4 font-mono font-bold text-indigo-400">
                    <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                      {item.item_type}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 max-w-sm">
                    <p className="font-semibold text-white">{item.title}</p>
                    <p className="text-slate-400 text-[11px] truncate">{item.description}</p>
                  </td>
                  <td className="py-3.5 px-4 font-mono text-[11px] text-cyan-400 max-w-xs truncate">
                    {JSON.stringify(item.payload)}
                  </td>
                  <td className="py-3.5 px-4">
                    <span className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                      item.status === 'APPROVED'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : item.status === 'REJECTED'
                        ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {item.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    {item.status === 'PENDING' ? (
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => approveMutation.mutate(item.id)}
                          className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold transition"
                        >
                          <CheckCircle2 className="h-3.5 w-3.5" /> Approve
                        </button>
                        <button
                          onClick={() => rejectMutation.mutate(item.id)}
                          className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 font-semibold transition"
                        >
                          <XCircle className="h-3.5 w-3.5" /> Reject
                        </button>
                      </div>
                    ) : (
                      <span className="text-slate-500 text-[11px]">Decided</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
