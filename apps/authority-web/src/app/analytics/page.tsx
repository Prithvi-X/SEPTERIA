'use client';

import React, { useState, useEffect } from 'react';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { api, SharedPatternItem, UnitWelfareSummary, GraphVisualizationData } from '@/lib/api';
import {
  BarChart3,
  EyeOff,
  Shield,
  Network,
  Users,
  AlertTriangle,
  MapPin,
  Clock,
  RefreshCw,
  Sparkles,
  Info,
  CheckCircle2,
  Lock,
  Compass,
  Layers
} from 'lucide-react';

export default function AnalyticsPage() {
  const [selectedUnit, setSelectedUnit] = useState<string>('BSF-BN-47');
  const [patterns, setPatterns] = useState<SharedPatternItem[]>([]);
  const [graphData, setGraphData] = useState<GraphVisualizationData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchGraphAndPatterns = async () => {
    try {
      setLoading(true);
      const res = await api.getUnitPatterns(selectedUnit);
      setPatterns(res.patterns || []);

      const gData = await api.getGraphVisualization();
      setGraphData(gData);
    } catch (err: any) {
      console.error('Failed to load graph/pattern data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraphAndPatterns();
  }, [selectedUnit]);

  return (
    <ProtectedRoute allowedRoles={['commander', 'welfare_officer', 'medical_officer', 'admin']}>
      <div className="space-y-6">
        {/* Header Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-5">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white tracking-tight">Command Force Intelligence</h1>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-900/60 text-emerald-300 border border-emerald-700/60 uppercase">
                Commander Aggregate View
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Unit-level recovery equilibrium, shared duty distress clusters, and tactical operational recommendations
            </p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={selectedUnit}
              onChange={(e) => setSelectedUnit(e.target.value)}
              className="bg-slate-900 text-xs font-semibold text-white border border-slate-700 rounded-lg px-3 py-1.5 focus:outline-none focus:border-blue-500"
            >
              <option value="BSF-BN-47">47th Battalion BSF (Tanot Sector)</option>
              <option value="CRPF-BN-88">88th Battalion CRPF (Active Ops)</option>
              <option value="ITBP-BN-12">12th Battalion ITBP (High Altitude)</option>
            </select>

            <button
              onClick={fetchGraphAndPatterns}
              className="p-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-300 hover:bg-slate-800"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Privacy Invariant Banner for Commander */}
        <div className="p-3.5 bg-blue-950/40 border border-blue-800/60 rounded-xl flex items-center justify-between gap-4 text-xs text-blue-200">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 bg-blue-600/20 text-blue-400 rounded-lg">
              <EyeOff className="w-4 h-4" />
            </div>
            <div>
              <span className="font-semibold text-white">Commander Privacy Boundary Enforced:</span> Individual personal biometrics, resting HR/HRV shifts, and private voice check-in details are strictly redacted. Only aggregated unit patterns and readiness trends are displayed.
            </div>
          </div>
          <span className="hidden sm:inline-block font-mono text-[10px] px-2 py-0.5 rounded bg-blue-900/60 border border-blue-700 text-blue-300">
            Zero Raw Biometrics
          </span>
        </div>

        {/* Unit Fleet Health & Readiness KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400">Platoon Headcount</span>
              <Users className="w-4 h-4 text-blue-400" />
            </div>
            <p className="text-2xl font-bold text-white mt-2">120 Jawans</p>
            <p className="text-[11px] text-slate-500 mt-0.5">100% Accounted in Battalion</p>
          </div>

          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400">Fleet Telemetry Health</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <p className="text-2xl font-bold text-emerald-400 mt-2">98.4%</p>
            <p className="text-[11px] text-slate-500 mt-0.5">Tactical BLE Wearable Completeness</p>
          </div>

          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400">Shared Distress Cluster</span>
              <AlertTriangle className="w-4 h-4 text-amber-400" />
            </div>
            <p className="text-2xl font-bold text-amber-300 mt-2">14 Affected</p>
            <p className="text-[11px] text-slate-500 mt-0.5">Night Shift Concurrent Strain</p>
          </div>

          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400">Operational Zone</span>
              <Compass className="w-4 h-4 text-purple-400" />
            </div>
            <p className="text-2xl font-bold text-purple-300 mt-2">Zone 2</p>
            <p className="text-[11px] text-slate-500 mt-0.5">Remote Border Outpost Line B</p>
          </div>
        </div>

        {/* Shared Recovery Distress Pattern Alert Card */}
        <div className="bg-slate-950/90 border border-amber-800/60 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-amber-600/20 text-amber-400 rounded-xl border border-amber-500/30">
                <Network className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-bold text-white">
                    Shared Platoon Recovery Strain Pattern
                  </h3>
                  <span className="font-mono text-xs px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800/60">
                    PAT-BSF-BN-47-ZONE_2-Night-1
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Contextual correlation: 14 Jawans exhibit concurrent recovery trajectory decline under identical shift constraints
                </p>
              </div>
            </div>

            <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-950/80 text-amber-300 border border-amber-800/80 self-start sm:self-auto">
              HIGH CONFIDENCE (70% PLATOON CORRELATION)
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-3.5 bg-slate-900/80 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase font-bold">Shared Context Conditions</span>
              <p className="font-semibold text-slate-200 mt-1">Zone 2 • Night Patrol (20:00 - 04:00) • Extreme Arid</p>
              <p className="text-[11px] text-slate-400 mt-1">Tanot Forward Line B Surveillance Section</p>
            </div>

            <div className="p-3.5 bg-slate-900/80 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase font-bold">Aggregated Physiological Trend</span>
              <p className="font-semibold text-amber-300 mt-1">Cumulative Sleep Deficit + Suppressed Autonomic Reserve</p>
              <p className="text-[11px] text-slate-400 mt-1">Average sleep duration: 3.8 hrs over 7 simulated days</p>
            </div>

            <div className="p-3.5 bg-slate-900/80 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase font-bold">Command Root-Cause Insight</span>
              <p className="font-semibold text-blue-300 mt-1">Environmental / Duty Burden (Not Individual Maladaptation)</p>
              <p className="text-[11px] text-slate-400 mt-1">Synchronized pattern indicates shift rotation fatigue</p>
            </div>
          </div>

          {/* Unit Action Recommendation */}
          <div className="p-4 bg-emerald-950/30 border border-emerald-800/60 rounded-xl">
            <div className="flex items-center gap-2 mb-1">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                Recommended Unit Commander Action:
              </span>
            </div>
            <p className="text-xs text-slate-200 leading-relaxed font-medium">
              &ldquo;Implement a 48-hour staggered shift rotation for Tanot Line B detachment. Stagger night watch shifts with Day Patrol sections to restore baseline sleep equilibrium.&rdquo;
            </p>
          </div>
        </div>

        {/* Contextual Personnel Graph Interactive Visualizer */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Network className="w-5 h-5 text-blue-400" />
                Contextual Personnel Graph Network (NetworkX Topology)
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Multi-dimensional relationships mapped across Unit, Zone, Shift, Duty, Environment, and Recovery Trajectory
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="inline-flex items-center gap-1 text-[11px] text-slate-400">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Unit Root
              </span>
              <span className="inline-flex items-center gap-1 text-[11px] text-slate-400">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Operational Context
              </span>
              <span className="inline-flex items-center gap-1 text-[11px] text-slate-400">
                <span className="w-2.5 h-2.5 rounded-full bg-red-400"></span> Strain Cluster
              </span>
              <span className="inline-flex items-center gap-1 text-[11px] text-slate-400">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span> Stable Jawans
              </span>
            </div>
          </div>

          {/* Interactive Graph SVG Canvas */}
          <div className="relative w-full h-80 bg-slate-900/90 rounded-xl border border-slate-800 flex items-center justify-center overflow-hidden">
            <svg className="w-full h-full" viewBox="-120 -120 240 240">
              {/* Central Unit Node */}
              <circle cx="0" cy="0" r="18" className="fill-blue-600/30 stroke-blue-400 stroke-2" />
              <text x="0" y="4" textAnchor="middle" className="text-[8px] fill-white font-bold">BSF-47</text>

              {/* Context Nodes */}
              {/* Zone 2 Node */}
              <line x1="0" y1="0" x2="-60" y2="-40" className="stroke-slate-700 stroke-1" />
              <circle cx="-60" cy="-40" r="12" className="fill-amber-600/30 stroke-amber-400 stroke-2" />
              <text x="-60" y="-37" textAnchor="middle" className="text-[6px] fill-amber-200 font-bold">Zone 2</text>

              {/* Night Shift Node */}
              <line x1="0" y1="0" x2="60" y2="-40" className="stroke-slate-700 stroke-1" />
              <circle cx="60" cy="-40" r="12" className="fill-purple-600/30 stroke-purple-400 stroke-2" />
              <text x="60" y="-37" textAnchor="middle" className="text-[6px] fill-purple-200 font-bold">Night</text>

              {/* Tanot Post Node */}
              <line x1="0" y1="0" x2="0" y2="60" className="stroke-slate-700 stroke-1" />
              <circle cx="0" cy="60" r="12" className="fill-cyan-600/30 stroke-cyan-400 stroke-2" />
              <text x="0" y="63" textAnchor="middle" className="text-[6px] fill-cyan-200 font-bold">Tanot</text>

              {/* Platoon Personnel Cluster Nodes (14 Jawans in strain cluster) */}
              {[...Array(14)].map((_, i) => {
                const angle = (i / 14) * Math.PI + Math.PI; // Top semi-circle
                const r = 90;
                const px = Math.cos(angle) * r;
                const py = Math.sin(angle) * r;
                return (
                  <g key={i}>
                    <line x1="-60" y1="-40" x2={px} y2={py} className="stroke-amber-900/60 stroke-1 stroke-dasharray-2" />
                    <line x1="60" y1="-40" x2={px} y2={py} className="stroke-purple-900/60 stroke-1 stroke-dasharray-2" />
                    <circle cx={px} cy={py} r="6" className="fill-red-900/60 stroke-red-400 stroke-1" />
                    <text x={px} y={py + 2} textAnchor="middle" className="text-[4px] fill-red-200">
                      J-{i + 1}
                    </text>
                  </g>
                );
              })}

              {/* 6 Stable Personnel Nodes (Bottom semi-circle) */}
              {[...Array(6)].map((_, i) => {
                const angle = (i / 6) * Math.PI; // Bottom semi-circle
                const r = 90;
                const px = Math.cos(angle) * r;
                const py = Math.sin(angle) * r;
                return (
                  <g key={i}>
                    <line x1="0" y1="60" x2={px} y2={py} className="stroke-slate-800 stroke-1" />
                    <circle cx={px} cy={py} r="6" className="fill-emerald-900/60 stroke-emerald-400 stroke-1" />
                    <text x={px} y={py + 2} textAnchor="middle" className="text-[4px] fill-emerald-200">
                      J-{i + 15}
                    </text>
                  </g>
                );
              })}
            </svg>

            <div className="absolute bottom-3 left-4 text-[10px] text-slate-500 font-mono">
              NetworkX Spring Layout Coordinates • Privacy Redacted View
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
