'use client';

import React, { useState, useEffect } from 'react';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { api, SharedPatternItem, GraphVisualizationData } from '@/lib/api';
import {
  Network,
  Users,
  AlertTriangle,
  RefreshCw,
  CheckCircle2,
  Lock
} from 'lucide-react';

export default function IntelligencePage() {
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
      console.error('Failed to load intelligence data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraphAndPatterns();
  }, [selectedUnit]);

  return (
    <ProtectedRoute allowedRoles={['commander', 'welfare_officer', 'medical_officer', 'admin']}>
      <div className="space-y-6 max-w-6xl">
        {/* Header Bar */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight uppercase">Unit Intelligence</h1>
            <p className="text-xs font-medium text-slate-400 mt-1 uppercase tracking-wider">
              Contextual Personnel Readiness & Shared Environmental Stressors
            </p>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={selectedUnit}
              onChange={(e) => setSelectedUnit(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-xs font-bold text-slate-300 rounded px-3 py-1.5 focus:outline-none uppercase tracking-wider"
            >
              <option value="BSF-BN-47">Battalion 47</option>
              <option value="CRPF-102">CRPF Unit 102</option>
            </select>
            <button
              onClick={fetchGraphAndPatterns}
              className="p-1.5 rounded bg-slate-800 text-slate-300 hover:text-white transition"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Operational Readiness Summary */}
        <div className="grid md:grid-cols-3 gap-4">
          <div className="p-4 bg-slate-950 border border-slate-800 rounded flex items-center justify-between">
            <div>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Unit Strength</p>
              <p className="text-xl font-bold text-slate-100">192</p>
            </div>
            <Users className="w-6 h-6 text-slate-600" />
          </div>
          <div className="p-4 bg-slate-950 border border-slate-800 rounded flex items-center justify-between">
            <div>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Baseline Stability</p>
              <p className="text-xl font-bold text-emerald-400">92.7%</p>
            </div>
            <CheckCircle2 className="w-6 h-6 text-emerald-600" />
          </div>
          <div className="p-4 bg-slate-950 border border-slate-800 rounded flex items-center justify-between">
            <div>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Identified Stress Patterns</p>
              <p className="text-xl font-bold text-amber-500">{patterns.length}</p>
            </div>
            <AlertTriangle className="w-6 h-6 text-amber-600" />
          </div>
        </div>

        {/* Shared Recovery Pattern & Why it matters */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-slate-950 border border-slate-800 rounded p-5 flex flex-col">
            <h2 className="text-xs font-bold text-slate-300 uppercase tracking-widest mb-4 flex items-center gap-2 border-b border-slate-800 pb-2">
              <Network className="w-4 h-4 text-slate-500" />
              Shared Recovery Patterns
            </h2>
            
            {loading ? (
              <div className="flex-1 flex items-center justify-center text-xs text-slate-500">Processing contextual links...</div>
            ) : patterns.length === 0 ? (
              <div className="flex-1 flex items-center justify-center text-xs text-slate-500">No significant shared patterns detected.</div>
            ) : (
              <div className="space-y-4">
                {patterns.map((pt, idx) => (
                  <div key={idx} className="bg-slate-900 border border-slate-700 p-4 rounded">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-sm font-bold text-white uppercase tracking-wider">{pt.pattern_type}</span>
                      <span className="text-xs font-bold text-amber-500 px-2 py-0.5 bg-amber-950 border border-amber-900 rounded">{pt.affected_personnel_count} Personnel</span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed mb-3">
                      {pt.authority_summary}
                    </p>
                    <div className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">
                      Confidence: <span className="text-slate-300">{pt.confidence_level}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-slate-950 border border-slate-800 rounded p-5">
            <h2 className="text-xs font-bold text-slate-300 uppercase tracking-widest mb-4 flex items-center gap-2 border-b border-slate-800 pb-2">
              <Lock className="w-4 h-4 text-slate-500" />
              Privacy & Invariant Note
            </h2>
            <div className="space-y-3 text-xs text-slate-400 leading-relaxed">
              <p>
                <strong>Non-Punitive Rule Enforced:</strong> Identified patterns aggregate physiological evidence to evaluate the operational environment, not to target individuals for punitive action.
              </p>
              <p>
                <strong>Contextual Links:</strong> The graph topology analyzes intersecting environments (zones, shifts, duties) to find root causes of collective physiological strain.
              </p>
              <p>
                Action taken based on these patterns should prioritize environmental mediation (e.g., duty rotation, sleep scheduling) rather than individual reprimand.
              </p>
            </div>
          </div>
        </div>

        {/* Contextual Network (Graph) as supporting evidence */}
        <div className="bg-slate-950 border border-slate-800 rounded p-5">
          <h2 className="text-xs font-bold text-slate-300 uppercase tracking-widest mb-4 flex items-center gap-2 border-b border-slate-800 pb-2">
            <Network className="w-4 h-4 text-slate-500" />
            Contextual Network Topology
          </h2>
          
          <div className="relative w-full h-80 bg-slate-900 rounded border border-slate-700 flex items-center justify-center overflow-hidden">
            <svg className="w-full h-full" viewBox="-120 -120 240 240">
              {/* Context Nodes & Edges */}
              <line x1="0" y1="0" x2="-60" y2="-40" className="stroke-slate-700 stroke-[0.5]" />
              <circle cx="-60" cy="-40" r="8" className="fill-slate-800 stroke-slate-500 stroke-1" />
              <text x="-60" y="-52" textAnchor="middle" className="text-[6px] fill-slate-300 font-medium tracking-widest uppercase">Zone 2</text>

              <line x1="0" y1="0" x2="60" y2="-40" className="stroke-slate-700 stroke-[0.5]" />
              <circle cx="60" cy="-40" r="8" className="fill-slate-800 stroke-slate-500 stroke-1" />
              <text x="60" y="-52" textAnchor="middle" className="text-[6px] fill-slate-300 font-medium tracking-widest uppercase">Night Shift</text>

              <line x1="-60" y1="-40" x2="-20" y2="-80" className="stroke-slate-700 stroke-[0.5] stroke-dasharray-[2,2]" />
              <circle cx="-20" cy="-80" r="4" className="fill-amber-500" />
              
              <line x1="-60" y1="-40" x2="-80" y2="-80" className="stroke-slate-700 stroke-[0.5] stroke-dasharray-[2,2]" />
              <circle cx="-80" cy="-80" r="4" className="fill-amber-500" />
              
              <line x1="60" y1="-40" x2="-20" y2="-80" className="stroke-slate-700 stroke-[0.5]" />
              <line x1="60" y1="-40" x2="40" y2="-80" className="stroke-slate-700 stroke-[0.5]" />
              <circle cx="40" cy="-80" r="4" className="fill-slate-400" />

              {/* Central Unit Node */}
              <circle cx="0" cy="0" r="14" className="fill-slate-900 stroke-slate-400 stroke-1" />
              <text x="0" y="2" textAnchor="middle" className="text-[7px] fill-white font-bold tracking-widest">BSF-47</text>
            </svg>
            <div className="absolute bottom-3 left-3 bg-slate-950/80 p-2 rounded border border-slate-800 text-[9px] text-slate-400 uppercase tracking-widest flex flex-col gap-1">
              <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-slate-400 rounded-full"></span> Personnel (Stable)</span>
              <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-amber-500 rounded-full"></span> Personnel (Strain)</span>
              <span className="flex items-center gap-1.5"><span className="w-2 h-2 bg-slate-800 border border-slate-500 rounded-full"></span> Context Node</span>
            </div>
          </div>
        </div>

      </div>
    </ProtectedRoute>
  );
}
