'use client';

import React, { useState } from 'react';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { useAuth } from '@/lib/auth';
import {
  HeartHandshake,
  Clock,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Shield,
  Stethoscope,
  Info,
  Calendar,
  ChevronDown
} from 'lucide-react';

// Using the same mock interfaces as before but rendering them strictly
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
  sleepDebtHours: number;
  hrShift: number;
  hrvCurrent: number;
  recommendedAction: string;
  acknowledged: boolean;
}

const DEMO_WELFARE_CASES: WelfareCase[] = [
  {
    id: 'case-01',
    personnelId: 'BSF-47-01',
    name: 'Constable Rajesh Kumar',
    rank: 'Constable',
    unit: 'BSF-BN-47',
    force: 'BSF',
    zone: 'Zone 2',
    duty: 'Border Patrol',
    shift: 'Night (20:00 - 04:00)',
    transitionStatus: 'Active Duty',
    welfareState: 'WELFARE_CHECK',
    compositeScore: 0.89,
    sleepDebtHours: 4.5,
    hrShift: +22,
    hrvCurrent: 24,
    recommendedAction: 'Schedule Immediate Wellness Consult',
    acknowledged: false,
  },
  {
    id: 'case-02',
    personnelId: 'BSF-47-14',
    name: 'Inspector Sunil Verma',
    rank: 'Inspector',
    unit: 'BSF-BN-47',
    force: 'BSF',
    zone: 'Zone 1',
    duty: 'Base Admin',
    shift: 'Day (08:00 - 16:00)',
    transitionStatus: 'Post-Leave (Day 3)',
    welfareState: 'AMBER',
    compositeScore: 0.72,
    sleepDebtHours: 2.5,
    hrShift: +15,
    hrvCurrent: 40,
    recommendedAction: 'Monitor Remotely; Post-leave transition',
    acknowledged: false,
  },
  {
    id: 'case-03',
    personnelId: 'CRPF-102-09',
    name: 'Constable Amit Singh',
    rank: 'Constable',
    unit: 'CRPF-102',
    force: 'CRPF',
    zone: 'Zone 3',
    duty: 'Static Guard',
    shift: 'Evening (16:00 - 00:00)',
    transitionStatus: 'Active Duty',
    welfareState: 'YELLOW',
    compositeScore: 0.58,
    sleepDebtHours: 1.5,
    hrShift: +8,
    hrvCurrent: 55,
    recommendedAction: 'No immediate action required',
    acknowledged: true,
  }
];

export default function WelfarePage() {
  const { user } = useAuth();
  const [cases, setCases] = useState<WelfareCase[]>(DEMO_WELFARE_CASES);
  const [selectedCaseId, setSelectedCaseId] = useState<string>(DEMO_WELFARE_CASES[0].id);
  const [showTechnical, setShowTechnical] = useState(false);

  const selectedCase = cases.find(c => c.id === selectedCaseId) || cases[0];

  const handleAcknowledge = () => {
    setCases(prev => prev.map(c => c.id === selectedCase.id ? { ...c, acknowledged: true } : c));
  };

  const getUrgencyColor = (state: string) => {
    switch (state) {
      case 'WELFARE_CHECK': return 'text-red-500 bg-red-500/10 border-red-500/20';
      case 'RED': return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 'AMBER': return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
      case 'YELLOW': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      default: return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
    }
  };

  return (
    <ProtectedRoute allowedRoles={['commander', 'welfare_officer', 'medical_officer', 'admin']}>
      <div className="space-y-6 max-w-7xl mx-auto h-[calc(100vh-6rem)] flex flex-col">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 border-b border-slate-800 pb-4 shrink-0">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight uppercase">Medical & Welfare Review</h1>
            <p className="text-xs font-medium text-slate-400 mt-1 uppercase tracking-wider">
              Confidential Personnel Recovery Monitoring
            </p>
          </div>
          <div className="text-xs text-slate-500 font-medium">
            <span className="uppercase tracking-wider">Role Authority: </span>
            <span className="text-white">{user?.role?.replace('_', ' ').toUpperCase()}</span>
          </div>
        </div>

        <div className="flex flex-1 gap-6 min-h-0">
          
          {/* Priority Queue (Left) */}
          <div className="w-1/3 flex flex-col bg-slate-950 border border-slate-800 rounded">
            <div className="p-4 border-b border-slate-800 bg-slate-900/50">
              <h2 className="text-xs font-bold text-slate-300 uppercase tracking-widest flex items-center justify-between">
                Review Queue
                <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded">{cases.filter(c => !c.acknowledged).length} Pending</span>
              </h2>
            </div>
            <div className="flex-1 overflow-y-auto p-2 space-y-2">
              {cases.map(c => (
                <button
                  key={c.id}
                  onClick={() => { setSelectedCaseId(c.id); setShowTechnical(false); }}
                  className={`w-full text-left p-4 rounded border transition-colors ${
                    selectedCaseId === c.id 
                      ? 'bg-slate-900 border-slate-700' 
                      : 'bg-transparent border-transparent hover:bg-slate-900/50 hover:border-slate-800'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-bold text-white">{c.personnelId}</span>
                    <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${getUrgencyColor(c.welfareState)}`}>
                      {c.welfareState.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400 font-medium">{c.name}</div>
                  <div className="text-[11px] text-slate-500 mt-2 flex items-center justify-between">
                    <span>{c.unit}</span>
                    {!c.acknowledged && <span className="w-2 h-2 rounded-full bg-blue-500"></span>}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Case Details (Right) */}
          <div className="flex-1 flex flex-col bg-slate-950 border border-slate-800 rounded overflow-y-auto">
            {/* Case Header */}
            <div className="p-6 border-b border-slate-800 bg-slate-900">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-white">{selectedCase.name}</h2>
                  <p className="text-xs font-medium text-slate-400 mt-1 uppercase tracking-wider">
                    {selectedCase.personnelId} • {selectedCase.rank} • {selectedCase.force}
                  </p>
                </div>
                <div className={`px-3 py-1.5 rounded border ${getUrgencyColor(selectedCase.welfareState)} text-xs font-bold uppercase tracking-wider`}>
                  {selectedCase.welfareState.replace('_', ' ')}
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4 mt-6">
                <div>
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Assigned Unit</p>
                  <p className="text-sm font-semibold text-slate-200">{selectedCase.unit}</p>
                </div>
                <div>
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Current Duty</p>
                  <p className="text-sm font-semibold text-slate-200">{selectedCase.duty}</p>
                </div>
                <div>
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Zone & Shift</p>
                  <p className="text-sm font-semibold text-slate-200">{selectedCase.zone} • {selectedCase.shift}</p>
                </div>
                <div>
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Status</p>
                  <p className="text-sm font-semibold text-slate-200">{selectedCase.transitionStatus}</p>
                </div>
              </div>
            </div>

            <div className="p-6 space-y-8 flex-1">
              
              {/* Why This Case Is Relevant */}
              <section>
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest mb-4 border-b border-slate-800 pb-2">
                  Physiological Evidence & Relevance
                </h3>
                <div className="bg-slate-900/50 p-5 rounded border border-slate-800">
                  <ul className="space-y-4 relative before:absolute before:inset-0 before:ml-2.5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-700 before:to-transparent">
                    <li className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                      <div className="flex items-center justify-center w-5 h-5 rounded-full border border-white bg-slate-800 text-slate-300 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                        <div className="w-1.5 h-1.5 bg-amber-500 rounded-full"></div>
                      </div>
                      <div className="w-[calc(100%-2rem)] md:w-[calc(50%-1.5rem)] bg-slate-950 p-4 rounded border border-slate-800 shadow">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-bold text-slate-200 text-xs">Sustained Sleep Debt</span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">
                          Personnel has accumulated {selectedCase.sleepDebtHours} hours of sleep debt over the past 3 days during Night Shift.
                        </p>
                      </div>
                    </li>
                    <li className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                      <div className="flex items-center justify-center w-5 h-5 rounded-full border border-white bg-slate-800 text-slate-300 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                        <div className="w-1.5 h-1.5 bg-amber-500 rounded-full"></div>
                      </div>
                      <div className="w-[calc(100%-2rem)] md:w-[calc(50%-1.5rem)] bg-slate-950 p-4 rounded border border-slate-800 shadow">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-bold text-slate-200 text-xs">Resting Heart Rate Elevated</span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">
                          Baseline resting HR has shifted by +{selectedCase.hrShift} bpm above normal, indicating incomplete physiological recovery.
                        </p>
                      </div>
                    </li>
                  </ul>
                </div>
              </section>

              {/* Recommended Response */}
              <section>
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest mb-4 border-b border-slate-800 pb-2">
                  Recommended Action
                </h3>
                <div className="bg-slate-900 border border-slate-700 p-5 rounded flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-slate-950 border border-slate-800 rounded">
                      <HeartHandshake className="w-6 h-6 text-blue-400" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-white">{selectedCase.recommendedAction}</p>
                      <p className="text-xs text-slate-400 mt-1">Based on established welfare protocols for sustained strain.</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <button 
                      onClick={handleAcknowledge}
                      disabled={selectedCase.acknowledged}
                      className="px-4 py-2 bg-slate-200 hover:bg-white text-slate-900 text-xs font-bold uppercase tracking-wider rounded transition disabled:opacity-50"
                    >
                      {selectedCase.acknowledged ? 'Acknowledged' : 'Acknowledge Case'}
                    </button>
                    <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold uppercase tracking-wider rounded border border-slate-700 transition">
                      Assign Check-in
                    </button>
                  </div>
                </div>
              </section>

              {/* Technical Evidence Accordion */}
              <section className="pt-4">
                <button
                  onClick={() => setShowTechnical(!showTechnical)}
                  className="w-full flex items-center justify-between p-4 bg-slate-900/50 border border-slate-800 rounded text-slate-400 hover:text-white transition"
                >
                  <span className="text-xs font-bold uppercase tracking-widest flex items-center gap-2">
                    <Info className="w-4 h-4" />
                    Technical Evidence Data
                  </span>
                  <ChevronDown className={`w-4 h-4 transition-transform ${showTechnical ? 'rotate-180' : ''}`} />
                </button>
                
                {showTechnical && (
                  <div className="p-5 mt-2 bg-slate-950 border border-slate-800 rounded space-y-4">
                    <p className="text-xs text-slate-500 italic mb-4">
                      Raw telemetry inputs provided for auditing purposes. Do not use for clinical diagnosis.
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="p-3 bg-slate-900 border border-slate-800 rounded">
                        <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">Composite Score</p>
                        <p className="text-sm font-mono text-slate-300">{selectedCase.compositeScore.toFixed(3)}</p>
                      </div>
                      <div className="p-3 bg-slate-900 border border-slate-800 rounded">
                        <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">HRV (ms)</p>
                        <p className="text-sm font-mono text-slate-300">{selectedCase.hrvCurrent}</p>
                      </div>
                      <div className="p-3 bg-slate-900 border border-slate-800 rounded">
                        <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">HR Shift</p>
                        <p className="text-sm font-mono text-slate-300">+{selectedCase.hrShift} bpm</p>
                      </div>
                      <div className="p-3 bg-slate-900 border border-slate-800 rounded">
                        <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">Sleep Debt</p>
                        <p className="text-sm font-mono text-slate-300">{selectedCase.sleepDebtHours} hr</p>
                      </div>
                    </div>
                  </div>
                )}
              </section>

            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
