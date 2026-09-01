'use client';

import React, { useState, useEffect } from 'react';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { api, MultimodalAssessment, PersonnelItem } from '@/lib/api';
import {
  HeartHandshake,
  ShieldCheck,
  Activity,
  UserCheck,
  TrendingDown,
  Clock,
  Mic,
  Network,
  AlertTriangle,
  CheckCircle2,
  FileText,
  ChevronRight,
  Shield,
  Stethoscope,
  Sparkles,
  Info
} from 'lucide-react';

interface WelfareCase {
  id: string;
  personnelId: string;
  name: string;
  rank: string;
  unit: string;
  force: string;
  zone: string;
  duty: string;
  shift: string;
  transitionStatus: string;
  welfareState: 'RED' | 'AMBER' | 'YELLOW' | 'GREEN' | 'WELFARE_CHECK';
  compositeScore: number;
  agreementIndex: number;
  sleepDebtHours: number;
  recoveryBurdenScore: number;
  hrShift: number;
  hrvCurrent: number;
  graphClusterId: string;
  graphAffectedCount: number;
  voiceDeviation: number;
  recommendedAction: string;
  acknowledged: boolean;
}

const DEMO_WELFARE_CASES: WelfareCase[] = [
  {
    id: 'case-01',
    personnelId: 'BSF-47-01',
    name: 'Constable Rajesh Kumar',
    rank: 'Constable (GD)',
    unit: 'BSF-BN-47',
    force: 'BSF',
    zone: 'Zone 2 (Border/Remote)',
    duty: 'Border Patrol',
    shift: 'Night (20:00 - 04:00)',
    transitionStatus: 'Post-Leave Day 3 / 14',
    welfareState: 'WELFARE_CHECK',
    compositeScore: 0.855,
    agreementIndex: 0.84,
    sleepDebtHours: 4.5,
    recoveryBurdenScore: 78,
    hrShift: 20.0,
    hrvCurrent: 24.0,
    graphClusterId: 'PAT-BSF-BN-47-ZONE_2-Night-1',
    graphAffectedCount: 14,
    voiceDeviation: 0.972,
    recommendedAction: 'Recommend authorized unit welfare check (Corroborating multi-stream strain across baseline, recovery, and operational indicators).',
    acknowledged: false,
  },
  {
    id: 'case-02',
    personnelId: 'CRPF-88-04',
    name: 'Head Constable Amit Sharma',
    rank: 'Head Constable',
    unit: 'CRPF-BN-88',
    force: 'CRPF',
    zone: 'Zone 1 (Active Ops)',
    duty: 'QRT Mobile Patrol',
    shift: 'Day',
    transitionStatus: 'Standard Deployment',
    welfareState: 'AMBER',
    compositeScore: 0.620,
    agreementIndex: 0.72,
    sleepDebtHours: 2.8,
    recoveryBurdenScore: 56,
    hrShift: 12.0,
    hrvCurrent: 38.0,
    graphClusterId: 'PAT-CRPF-BN-88-ZONE_1-Day-2',
    graphAffectedCount: 6,
    voiceDeviation: 0.410,
    recommendedAction: 'Recommend designated section peer check and duty rotation review.',
    acknowledged: true,
  },
  {
    id: 'case-03',
    personnelId: 'ITBP-12-09',
    name: 'Constable Tenzing Norbu',
    rank: 'Constable (GD)',
    unit: 'ITBP-BN-12',
    force: 'ITBP',
    zone: 'Zone 2 (High Altitude)',
    duty: 'High Altitude Guard',
    shift: 'Night',
    transitionStatus: 'Post-Leave Day 8 / 14',
    welfareState: 'YELLOW',
    compositeScore: 0.440,
    agreementIndex: 0.65,
    sleepDebtHours: 1.5,
    recoveryBurdenScore: 42,
    hrShift: 6.0,
    hrvCurrent: 52.0,
    graphClusterId: 'NONE',
    graphAffectedCount: 0,
    voiceDeviation: 0.200,
    recommendedAction: 'Homeostasis maintained within altitude operational bounds; continue routine monitoring.',
    acknowledged: false,
  },
];

export default function WelfarePage() {
  const [cases, setCases] = useState<WelfareCase[]>(DEMO_WELFARE_CASES);
  const [selectedCase, setSelectedCase] = useState<WelfareCase>(DEMO_WELFARE_CASES[0]);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const handleAcknowledge = (caseId: string) => {
    setCases((prev) =>
      prev.map((c) => (c.id === caseId ? { ...c, acknowledged: true } : c))
    );
    if (selectedCase.id === caseId) {
      setSelectedCase((prev) => ({ ...prev, acknowledged: true }));
    }
    setActionSuccess('Case acknowledged. Logged to Unit Medical Officer audit record.');
    setTimeout(() => setActionSuccess(null), 3500);
  };

  const handleAction = (actionText: string) => {
    setActionSuccess(`Action initiated: "${actionText}". Notification sent to designated personnel.`);
    setTimeout(() => setActionSuccess(null), 4000);
  };

  const getStateBadge = (state: string) => {
    switch (state) {
      case 'RED':
      case 'WELFARE_CHECK':
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-red-950/80 text-red-300 border border-red-800/80 flex items-center gap-1.5 animate-pulse">
            <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
            ELEVATED WELFARE CONCERN
          </span>
        );
      case 'AMBER':
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-950/80 text-amber-300 border border-amber-800/80 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            MODERATE STRAIN (MONITOR)
          </span>
        );
      case 'YELLOW':
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-yellow-950/80 text-yellow-300 border border-yellow-800/80 flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-yellow-400" />
            MILD ELEVATION (ROUTINE)
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-800/80 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            RECOVERY EQUILIBRIUM
          </span>
        );
    }
  };

  return (
    <ProtectedRoute allowedRoles={['welfare_officer', 'medical_officer', 'admin']}>
      <div className="space-y-6">
        {/* Header Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-5">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white tracking-tight">Medical & Welfare Case Review</h1>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-900/60 text-blue-300 border border-blue-700/60 uppercase">
                Confidential Officer View
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Multi-stream evidence synthesis, personal autonomic deviation tracking, and human-in-the-loop care protocols
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-950/60 text-emerald-300 border border-emerald-800/60 text-xs">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Medical RBAC Active</span>
            </div>
          </div>
        </div>

        {/* Action Toast Alert */}
        {actionSuccess && (
          <div className="p-3.5 bg-emerald-950/80 border border-emerald-800/80 rounded-xl text-xs text-emerald-200 flex items-center gap-2 animate-in fade-in">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>{actionSuccess}</span>
          </div>
        )}

        {/* Main Grid: Cases Queue (Left) & Detailed Multi-Stream Review (Right) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Active Cases Triage Queue */}
          <div className="lg:col-span-4 space-y-3">
            <div className="flex items-center justify-between px-1">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Priority Welfare Queue ({cases.length})
              </span>
              <span className="text-[11px] text-slate-500 font-mono">Real-Time</span>
            </div>

            <div className="space-y-2">
              {cases.map((c) => {
                const isSelected = selectedCase.id === c.id;
                return (
                  <div
                    key={c.id}
                    onClick={() => setSelectedCase(c)}
                    className={`p-4 rounded-xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-slate-900 border-blue-500 shadow-md shadow-blue-500/10'
                        : 'bg-slate-950/80 border-slate-800 hover:border-slate-700 hover:bg-slate-900/60'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-bold text-white">{c.name}</h4>
                          <span className="text-[11px] text-slate-400 font-mono">({c.personnelId})</span>
                        </div>
                        <p className="text-xs text-slate-400 mt-0.5">
                          {c.rank} • {c.unit} ({c.force})
                        </p>
                      </div>
                      <ChevronRight className={`w-4 h-4 ${isSelected ? 'text-blue-400' : 'text-slate-600'}`} />
                    </div>

                    <div className="mt-3 flex items-center justify-between">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        c.welfareState === 'WELFARE_CHECK' || c.welfareState === 'RED'
                          ? 'bg-red-950/80 text-red-300 border border-red-800/60'
                          : c.welfareState === 'AMBER'
                          ? 'bg-amber-950/80 text-amber-300 border border-amber-800/60'
                          : 'bg-yellow-950/80 text-yellow-300 border border-yellow-800/60'
                      }`}>
                        {c.welfareState.replace('_', ' ')}
                      </span>

                      <span className="text-[11px] text-slate-400 font-mono">
                        Score: {(c.compositeScore * 100).toFixed(0)}%
                      </span>
                    </div>

                    <div className="mt-2 text-[11px] text-slate-500 truncate">
                      Context: {c.zone} • {c.shift}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Column: Case Deep-Dive & Multi-Stream Breakdown */}
          <div className="lg:col-span-8 space-y-5">
            <div className="bg-slate-950/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
              {/* Personnel Summary Banner */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
                <div>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-600/20 border border-blue-500/40 text-blue-400 flex items-center justify-center font-bold text-sm">
                      {selectedCase.name.split(' ').map((n) => n[0]).join('')}
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        {selectedCase.name}
                        <span className="text-xs text-slate-400 font-mono font-normal">[{selectedCase.personnelId}]</span>
                      </h3>
                      <p className="text-xs text-slate-400">
                        {selectedCase.rank} • {selectedCase.unit} ({selectedCase.force}) • Tanot Forward Sector
                      </p>
                    </div>
                  </div>
                </div>

                <div className="text-right flex flex-col sm:items-end gap-1.5">
                  {getStateBadge(selectedCase.welfareState)}
                  <span className="text-[11px] text-slate-400">
                    Evidence Agreement Index: <strong>{(selectedCase.agreementIndex * 100).toFixed(0)}%</strong>
                  </span>
                </div>
              </div>

              {/* Authoritative Operational Context Ribbon */}
              <div className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2.5">
                  <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-blue-400" />
                    Authoritative Operational Context (Command-Assigned)
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">Source: Authority Context Engine</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800">
                    <span className="text-[10px] text-slate-500 uppercase">Operational Zone</span>
                    <p className="font-semibold text-amber-300 mt-0.5">{selectedCase.zone}</p>
                  </div>
                  <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800">
                    <span className="text-[10px] text-slate-500 uppercase">Duty & Shift</span>
                    <p className="font-semibold text-slate-200 mt-0.5">{selectedCase.duty} ({selectedCase.shift})</p>
                  </div>
                  <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800">
                    <span className="text-[10px] text-slate-500 uppercase">Deployment</span>
                    <p className="font-semibold text-purple-300 mt-0.5">Temporary Assignment</p>
                  </div>
                  <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800">
                    <span className="text-[10px] text-slate-500 uppercase">Transition State</span>
                    <p className="font-semibold text-blue-300 mt-0.5">{selectedCase.transitionStatus}</p>
                  </div>
                </div>
              </div>

              {/* Multi-Stream Evidence Breakdown (Phases 1-8 Convergence) */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                    Multimodal Evidence Streams (5 Independent Sources)
                  </h4>
                  <span className="text-[11px] text-slate-500 font-mono">Tri-Layer Synthesis</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  {/* Stream 1: Wearable Physiological ML */}
                  <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-blue-300 flex items-center gap-1.5">
                        <Activity className="w-3.5 h-3.5 text-blue-400" />
                        1. Physiological ML Core
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800/60">
                        XGBoost (WESAD/PhysioNet)
                      </span>
                    </div>
                    <div className="flex items-baseline gap-2 mt-1">
                      <span className="text-xl font-bold text-white">
                        {(selectedCase.compositeScore).toFixed(2)}
                      </span>
                      <span className="text-xs text-slate-400">P(physio stress probability)</span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      Kinetic motion disambiguated (ACC energy &lt; 2.0 m/s²). Signal Quality SQI: <strong>0.95 (Good)</strong>.
                    </p>
                  </div>

                  {/* Stream 2: Autonomic Personal Baseline */}
                  <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-amber-300 flex items-center gap-1.5">
                        <TrendingDown className="w-3.5 h-3.5 text-amber-400" />
                        2. Autonomic Personal Baseline
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800/60">
                        Median / MAD Shift
                      </span>
                    </div>
                    <div className="flex items-baseline gap-2 mt-1">
                      <span className="text-xl font-bold text-amber-300">
                        +{selectedCase.hrShift} bpm
                      </span>
                      <span className="text-xs text-slate-400">Resting HR Shift (HRV: {selectedCase.hrvCurrent} ms)</span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      Autonomic strain z-score: <strong>z = +2.45</strong> (Suppressed autonomic reserve relative to soldier baseline).
                    </p>
                  </div>

                  {/* Stream 3: Multi-Day Recovery Trajectory */}
                  <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-purple-300 flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5 text-purple-400" />
                        3. Recovery Debt & Sleep
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-purple-950 text-purple-400 border border-purple-800/60">
                        7-Day Multi-Window
                      </span>
                    </div>
                    <div className="flex items-baseline gap-2 mt-1">
                      <span className="text-xl font-bold text-purple-300">
                        {selectedCase.sleepDebtHours}h
                      </span>
                      <span className="text-xs text-slate-400">Cumulative Sleep Debt (Burden: {selectedCase.recoveryBurdenScore}%)</span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      Trajectory status: <strong className="text-amber-400">DETERIORATING</strong> across 7 consecutive night rotations.
                    </p>
                  </div>

                  {/* Stream 4: Contextual Personnel Graph */}
                  <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-emerald-300 flex items-center gap-1.5">
                        <Network className="w-3.5 h-3.5 text-emerald-400" />
                        4. Contextual Graph Cluster
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                        NetworkX Platoon Correlation
                      </span>
                    </div>
                    <div className="flex items-baseline gap-2 mt-1">
                      <span className="text-xl font-bold text-emerald-300">
                        {selectedCase.graphAffectedCount} Jawans
                      </span>
                      <span className="text-xs text-slate-400">Co-occurring in Unit 47</span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      Cluster ID: <span className="font-mono text-slate-300">{selectedCase.graphClusterId}</span> (Identical night exposure).
                    </p>
                  </div>
                </div>

                {/* Stream 5: Voluntary Voice Acoustic Evidence */}
                <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl flex items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Mic className="w-3.5 h-3.5 text-cyan-400" />
                      <span className="text-xs font-semibold text-cyan-300">5. Voluntary Voice Check-In (Acoustic Pitch & Pause Dynamics)</span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/60">
                        Voluntary • In-Memory
                      </span>
                    </div>
                    <p className="text-xs text-slate-400">
                      Acoustic shifts observed: Elevated mean fundamental pitch ($F_0$), increased pause duration ratio. Zero raw audio retained.
                    </p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className="text-base font-bold text-cyan-300">
                      {(selectedCase.voiceDeviation * 100).toFixed(0)}%
                    </span>
                    <p className="text-[10px] text-slate-500">Acoustic Shift Index</p>
                  </div>
                </div>
              </div>

              {/* Non-Punitive Human Welfare Action Recommendation */}
              <div className="p-4 bg-blue-950/40 border border-blue-800/80 rounded-xl space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Stethoscope className="w-4 h-4 text-blue-400" />
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                      Human-in-the-Loop Welfare Recommendation
                    </h4>
                  </div>
                  <span className="text-[10px] text-blue-300 font-mono">Non-Punitive Action Protocol</span>
                </div>
                <p className="text-xs text-slate-200 leading-relaxed font-medium">
                  &ldquo;{selectedCase.recommendedAction}&rdquo;
                </p>

                {/* Care Action Buttons */}
                <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-blue-900/60">
                  <button
                    disabled={selectedCase.acknowledged}
                    onClick={() => handleAcknowledge(selectedCase.id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium transition disabled:opacity-50"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>{selectedCase.acknowledged ? 'Acknowledged' : 'Acknowledge Case'}</span>
                  </button>

                  <button
                    onClick={() => handleAction('Designated Section Peer Welfare Check')}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition border border-slate-700"
                  >
                    <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Assign Peer Check</span>
                  </button>

                  <button
                    onClick={() => handleAction('Medical Officer Tele-Consultation Scheduled')}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition border border-slate-700"
                  >
                    <Stethoscope className="w-3.5 h-3.5 text-purple-400" />
                    <span>Request MO Review</span>
                  </button>

                  <button
                    onClick={() => handleAction('Rest & Recovery Rotation Scheduled')}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition border border-slate-700"
                  >
                    <Clock className="w-3.5 h-3.5 text-amber-400" />
                    <span>Schedule Recovery Window</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
