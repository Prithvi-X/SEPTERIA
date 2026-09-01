'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { useAuth } from '@/lib/auth';
import { api, DashboardMetrics, AuditLogItem, EdgeFleetOverview } from '@/lib/api';
import { RefreshCw, AlertCircle } from 'lucide-react';

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
      <div className="space-y-8 max-w-5xl">
        {/* Header - Serious, Operational */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">SEPTERIA</h1>
            <p className="text-xs font-medium text-slate-400 mt-1 uppercase tracking-wider">
              Personnel Welfare & Operational Readiness
            </p>
            <div className="mt-3 text-sm text-slate-300 font-medium">
              BSF · Battalion 47 <span className="mx-2 text-slate-600">|</span> Tanot Forward Sector
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <span className="text-slate-500 font-medium">{user?.role?.replace('_', ' ').toUpperCase()}</span>
            <button
              onClick={fetchDashboardData}
              className="flex items-center gap-1.5 text-slate-400 hover:text-white transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-950/40 border border-red-900/50 rounded text-red-400 text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {/* Unified Operational Summary Strip */}
        <div className="grid grid-cols-2 md:grid-cols-5 border border-slate-800 divide-y md:divide-y-0 md:divide-x divide-slate-800 rounded bg-slate-900/50">
          <div className="p-4 flex flex-col">
            <span className="text-2xl font-bold text-slate-100">{metrics?.total_personnel ?? '-'}</span>
            <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider mt-1">Personnel</span>
          </div>
          <div className="p-4 flex flex-col">
            <span className="text-2xl font-bold text-emerald-400">{edgeOverview?.total_registered_devices ? ((edgeOverview.active_devices / edgeOverview.total_registered_devices) * 100).toFixed(1) + '%' : '-'}</span>
            <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider mt-1">Telemetry Available</span>
          </div>
          <div className="p-4 flex flex-col">
            <span className="text-2xl font-bold text-amber-500">14</span>
            <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider mt-1">Recovery Concerns</span>
          </div>
          <div className="p-4 flex flex-col">
            <span className="text-2xl font-bold text-slate-300">{metrics?.personnel_in_transition ?? '-'}</span>
            <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider mt-1">Post-leave Transitions</span>
          </div>
          <div className="p-4 flex flex-col col-span-2 md:col-span-1">
            <span className="text-2xl font-bold text-blue-400">{metrics?.active_temporary_assignments ?? '-'}</span>
            <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider mt-1">Active Temp Deployment</span>
          </div>
        </div>

        {/* ATTENTION REQUIRED */}
        <div>
          <h2 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-2 mb-4">
            Attention Required
          </h2>
          <div className="bg-slate-900 border border-slate-700 p-6 rounded flex flex-col sm:flex-row gap-6 justify-between items-start">
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-amber-500 font-semibold">
                <AlertCircle className="w-5 h-5" />
                <span className="text-base">14 personnel show a shared recovery decline</span>
              </div>
              <p className="text-sm text-slate-300 leading-relaxed max-w-2xl">
                <span className="font-semibold text-white">Zone 2 · Night deployment</span>
                <br />
                Observed over the last 3 days.
                <br />
                Reduced recovery opportunity combined with increased workload is showing persistent physiological deterioration across the unit.
              </p>
            </div>
            <Link 
              href="/analytics" 
              className="shrink-0 bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium px-4 py-2 rounded transition border border-slate-700"
            >
              Review pattern
            </Link>
          </div>
        </div>

        {/* CURRENT OPERATIONS & RECENT CHANGES */}
        <div className="grid md:grid-cols-2 gap-8">
          {/* Current Operations */}
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-2 mb-4">
              Current Operations
            </h2>
            <div className="bg-slate-900/50 border border-slate-800 rounded flex flex-col divide-y divide-slate-800/50">
              <div className="px-4 py-3 flex justify-between items-center">
                <span className="text-sm font-medium text-slate-300">Zone 1</span>
                <span className="text-sm font-bold text-slate-100">{metrics?.zone_distribution?.zone_1 ?? 30} personnel</span>
              </div>
              <div className="px-4 py-3 flex justify-between items-center">
                <span className="text-sm font-medium text-slate-300">Zone 2</span>
                <span className="text-sm font-bold text-slate-100">{metrics?.zone_distribution?.zone_2 ?? 162} personnel</span>
              </div>
              <div className="px-4 py-3 flex justify-between items-center text-slate-500">
                <span className="text-sm font-medium">Zone 3</span>
                <span className="text-sm font-bold">{metrics?.zone_distribution?.zone_3 ?? 0} personnel</span>
              </div>
            </div>
          </div>

          {/* Recent Changes */}
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-2 mb-4">
              Recent Changes
            </h2>
            <div className="space-y-4">
              <div className="flex gap-3 items-start">
                <div className="w-2 h-2 mt-1.5 rounded-full bg-blue-500 shrink-0"></div>
                <div>
                  <p className="text-sm text-slate-200">Temporary deployment active in Zone 2</p>
                  <p className="text-xs text-slate-500 mt-0.5">Authoritative reassignment initiated 12 hours ago</p>
                </div>
              </div>
              <div className="flex gap-3 items-start">
                <div className="w-2 h-2 mt-1.5 rounded-full bg-emerald-500 shrink-0"></div>
                <div>
                  <p className="text-sm text-slate-200">{metrics?.personnel_in_transition ?? 4} personnel entered post-leave reintegration</p>
                  <p className="text-xs text-slate-500 mt-0.5">Standard 14-day monitoring phase applied</p>
                </div>
              </div>
              <div className="flex gap-3 items-start">
                <div className="w-2 h-2 mt-1.5 rounded-full bg-slate-600 shrink-0"></div>
                <div>
                  <p className="text-sm text-slate-200">Night patrol rotation expanded</p>
                  <p className="text-xs text-slate-500 mt-0.5">Battalion 47 schedules updated</p>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </ProtectedRoute>
  );
}
