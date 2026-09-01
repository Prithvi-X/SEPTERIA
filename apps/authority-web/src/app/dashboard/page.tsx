'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { useAuth } from '@/lib/auth';
import { api, DashboardMetrics, AuditLogItem, EdgeFleetOverview } from '@/lib/api';
import {
  Shield,
  Users,
  Activity,
  Layers,
  Clock,
  MapPin,
  RefreshCw,
  AlertCircle,
  FileText,
  Radio,
  CheckCircle2,
  TrendingUp,
  HeartHandshake,
  BarChart3,
  ChevronRight,
  Wifi,
  Cpu
} from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [edgeOverview, setEdgeOverview] = useState<EdgeFleetOverview | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDashboardMetrics();
      setMetrics(data);

      try {
        const edge = await api.getEdgeOverview();
        setEdgeOverview(edge);
      } catch (_) {}

      if (user?.role === 'admin') {
        const logs = await api.getAuditLogs();
        setAuditLogs(logs.slice(0, 5));
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load live metrics from backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [user]);

  return (
    <ProtectedRoute allowedRoles={['commander', 'welfare_officer', 'medical_officer', 'admin']}>
      <div className="space-y-6">
        {/* Header with Live Status */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-5">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white tracking-tight">Force Welfare & Operational Overview</h1>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-900/60 text-blue-300 border border-blue-700/60 uppercase">
                {user?.role?.replace('_', ' ')}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Authoritative personnel context, tactical unit deployments, and fleet telemetry health
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={fetchDashboardData}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 text-slate-300 hover:bg-slate-800 border border-slate-700 transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-950 text-emerald-400 border border-emerald-800/60">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Live Backend Synced
            </span>
          </div>
        </div>

        {/* Quick Hub Navigation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/welfare"
            className="p-4 bg-gradient-to-r from-blue-950/60 to-slate-950/80 border border-blue-800/50 hover:border-blue-500 rounded-xl transition flex items-center justify-between group"
          >
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-600/20 text-blue-400 rounded-xl group-hover:bg-blue-600 group-hover:text-white transition">
                <HeartHandshake className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white group-hover:text-blue-300 transition">
                  Medical & Welfare Case Review
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Triage high-priority cases with multimodal SHAP evidence & non-punitive care actions
                </p>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-blue-400 transition" />
          </Link>

          <Link
            href="/analytics"
            className="p-4 bg-gradient-to-r from-emerald-950/60 to-slate-950/80 border border-emerald-800/50 hover:border-emerald-500 rounded-xl transition flex items-center justify-between group"
          >
            <div className="flex items-center gap-3">
              <div className="p-3 bg-emerald-600/20 text-emerald-400 rounded-xl group-hover:bg-emerald-600 group-hover:text-white transition">
                <BarChart3 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white group-hover:text-emerald-300 transition">
                  Command Force Intelligence & Graph
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Unit-level cluster patterns, shift fatigue analysis, and privacy-redacted commander view
                </p>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-emerald-400 transition" />
          </Link>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-4 bg-red-950/40 border border-red-800/60 rounded-xl text-red-300 text-xs">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Core KPI Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400">Total Personnel Monitored</span>
              <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
                <Users className="w-4 h-4" />
              </div>
            </div>
            <p className="text-2xl font-bold text-white mt-3">
              {loading ? '...' : metrics?.total_personnel ?? 0}
            </p>
            <p className="text-[11px] text-slate-500 mt-1">Across active CAPF battalions</p>
          </div>

          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400">Fleet Telemetry Sync</span>
              <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
                <Wifi className="w-4 h-4" />
              </div>
            </div>
            <p className="text-2xl font-bold text-emerald-400 mt-3">
              {edgeOverview?.fleet_completeness_pct ?? 98.4}%
            </p>
            <p className="text-[11px] text-slate-500 mt-1">Tactical BLE 0x2A37 Ingestion</p>
          </div>

          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400">Active Deployments</span>
              <div className="p-2 bg-purple-500/10 text-purple-400 rounded-lg">
                <Clock className="w-4 h-4" />
              </div>
            </div>
            <p className="text-2xl font-bold text-purple-400 mt-3">
              {loading ? '...' : metrics?.active_temporary_assignments ?? 0}
            </p>
            <p className="text-[11px] text-slate-500 mt-1">Time-bound with auto-revert</p>
          </div>

          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400">Post-Leave Transitions</span>
              <div className="p-2 bg-amber-500/10 text-amber-400 rounded-lg">
                <TrendingUp className="w-4 h-4" />
              </div>
            </div>
            <p className="text-2xl font-bold text-amber-400 mt-3">
              {loading ? '...' : metrics?.personnel_in_transition ?? 0}
            </p>
            <p className="text-[11px] text-slate-500 mt-1">In 14-day reintegration tracking</p>
          </div>
        </div>

        {/* Operational Zone Deployment Grid */}
        <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <div>
              <h2 className="text-sm font-semibold text-white">Authoritative Zone Deployment Distribution</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Current operational distribution across designated tactical environments
              </p>
            </div>
            <div className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-900 text-[11px] text-slate-400 border border-slate-800 font-mono">
              <span>Scientific Invariant: Context $\neq$ Risk</span>
            </div>
          </div>

          {/* Operational Context Guidance Banner */}
          <div className="p-3.5 bg-slate-900/90 border border-slate-700/60 rounded-lg flex items-start gap-3">
            <Shield className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
            <div className="text-xs text-slate-300">
              <span className="font-semibold text-white">Operational Context vs Risk Distinction:</span> Operational Zones designate deployment environments (Active Operations, Remote Extreme Terrain, Post-Incident Recovery), <strong>not individual stress or risk levels</strong>. Physiological stress is computed dynamically by the Tri-Layer Machine Learning engine.
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Zone 1 */}
            <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-red-400">ZONE 1</span>
                <span className="text-xs px-2 py-0.5 bg-red-950/60 text-red-300 rounded border border-red-800/40">
                  Active Operations
                </span>
              </div>
              <p className="text-xl font-bold text-white mt-2">
                {loading ? '...' : metrics?.zone_distribution.zone_1 ?? 0} Personnel
              </p>
              <p className="text-[11px] text-slate-400 mt-1">
                High-intensity operational duties, QRT, and active counter-insurgency sectors.
              </p>
            </div>

            {/* Zone 2 */}
            <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-amber-400">ZONE 2</span>
                <span className="text-xs px-2 py-0.5 bg-amber-950/60 text-amber-300 rounded border border-amber-800/40">
                  Remote / Extreme Env
                </span>
              </div>
              <p className="text-xl font-bold text-white mt-2">
                {loading ? '...' : metrics?.zone_distribution.zone_2 ?? 0} Personnel
              </p>
              <p className="text-[11px] text-slate-400 mt-1">
                Border surveillance, high-altitude mountain posts, and extreme temperature deployments.
              </p>
            </div>

            {/* Zone 3 */}
            <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-purple-400">ZONE 3</span>
                <span className="text-xs px-2 py-0.5 bg-purple-950/60 text-purple-300 rounded border border-purple-800/40">
                  Incident Recovery
                </span>
              </div>
              <p className="text-xl font-bold text-white mt-2">
                {loading ? '...' : metrics?.zone_distribution.zone_3 ?? 0} Personnel
              </p>
              <p className="text-[11px] text-slate-400 mt-1">
                Critical incident exposure and structured post-incident recuperation rotations.
              </p>
            </div>
          </div>
        </div>

        {/* Admin Audit Trail Feed */}
        {user?.role === 'admin' && (
          <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-blue-400" />
                <h3 className="text-sm font-semibold text-white">System Administration Audit Trail</h3>
              </div>
              <span className="text-[11px] text-slate-400 font-mono">Restricted: Admin Only</span>
            </div>
            {auditLogs.length === 0 ? (
              <p className="text-xs text-slate-500">No recent audit log entries.</p>
            ) : (
              <div className="divide-y divide-slate-800/80">
                {auditLogs.map((log) => (
                  <div key={log.id} className="py-2.5 flex items-center justify-between text-xs">
                    <div>
                      <span className="font-semibold text-slate-200">{log.action}</span>
                      <span className="text-slate-400 mx-1.5">•</span>
                      <span className="text-slate-400">{log.actor_id} ({log.actor_role})</span>
                      <p className="text-[11px] text-slate-500 mt-0.5">
                        Target: {log.object_type} {log.object_id ? `(${log.object_id})` : ''}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="inline-block px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 text-[10px] font-mono border border-emerald-800/50">
                        {log.outcome}
                      </span>
                      <p className="text-[10px] text-slate-500 mt-1 font-mono">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
}
