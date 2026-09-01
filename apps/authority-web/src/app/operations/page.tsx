'use client';

import React, { useEffect, useState } from 'react';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { useAuth } from '@/lib/auth';
import { api, OperationalContextItem, UnitItem } from '@/lib/api';
import {
  MapPin,
  Plus,
  Clock,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  X,
  Shield,
  Timer
} from 'lucide-react';

export default function OperationsPage() {
  const { user } = useAuth();
  const [operations, setOperations] = useState<OperationalContextItem[]>([]);
  const [units, setUnits] = useState<UnitItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Assignment Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [name, setName] = useState('Border Deployment Alpha');
  const [targetUnit, setTargetUnit] = useState('BSF-BN-47');
  const [zone, setZone] = useState('Zone 2');
  const [dutyType, setDutyType] = useState('Border Patrol');
  const [shift, setShift] = useState('Night (20:00 - 04:00)');
  const [location, setLocation] = useState('Tanot Sector Border Line');
  const [environment, setEnvironment] = useState('High Heat / Desert Arid');
  const [durationDays, setDurationDays] = useState(7);
  const [autoRevert, setAutoRevert] = useState(true);
  const [notes, setNotes] = useState('Tactical summer heat border surveillance rotation.');
  const [submitting, setSubmitting] = useState(false);

  // Auto-revert trigger simulation
  const [reverting, setReverting] = useState(false);

  const fetchOperationsData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [opsData, unitsData] = await Promise.all([
        api.getOperations(),
        api.getUnits(),
      ]);
      setOperations(opsData);
      setUnits(unitsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load operational deployments.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOperationsData();
  }, []);

  const handleCreateAssignment = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const res = await api.bulkAssign({
        assignment_name: name,
        unit_id: targetUnit,
        zone,
        duty_type: dutyType,
        shift,
        location,
        environment,
        duration_days: Number(durationDays),
        auto_revert: autoRevert,
        notes,
      });
      setActionSuccess(res.message);
      setShowCreateModal(false);
      fetchOperationsData();
      setTimeout(() => setActionSuccess(null), 5000);
    } catch (err: any) {
      setError(err.message || 'Failed to create operational assignment.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEvaluateReversions = async () => {
    setReverting(true);
    setError(null);
    try {
      const res = await api.evaluateReversions();
      setActionSuccess(res.message);
      fetchOperationsData();
      setTimeout(() => setActionSuccess(null), 5000);
    } catch (err: any) {
      setError(err.message || 'Failed to evaluate automatic reversions.');
    } finally {
      setReverting(false);
    }
  };

  const isCommanderOrAdmin = user?.role === 'commander' || user?.role === 'admin';

  return (
    <ProtectedRoute allowedRoles={['commander', 'welfare_officer', 'medical_officer', 'admin']}>
      <div className="space-y-6 max-w-6xl">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight uppercase">Operational Deployments</h1>
            <p className="text-xs font-medium text-slate-400 mt-1 uppercase tracking-wider">
              Authoritative Unit Assignments & Auto-Reverting Schedules
            </p>
          </div>
          <div className="flex items-center gap-3">
            {isCommanderOrAdmin && (
              <button
                onClick={handleEvaluateReversions}
                disabled={reverting}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-medium border border-slate-700 transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${reverting ? 'animate-spin' : ''}`} />
                <span>Simulate Auto-Reversion</span>
              </button>
            )}
            {isCommanderOrAdmin ? (
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center gap-2 px-3.5 py-1.5 bg-slate-200 hover:bg-white text-slate-900 rounded text-xs font-bold transition shadow-sm uppercase tracking-wider"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>New Assignment</span>
              </button>
            ) : (
              <span className="text-xs text-slate-400 italic">Read-Only View</span>
            )}
          </div>
        </div>

        {/* Global Notifications */}
        {actionSuccess && (
          <div className="flex items-center justify-between p-4 bg-emerald-950/40 border border-emerald-900/50 rounded text-emerald-400 text-sm">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              <span className="font-medium">{actionSuccess}</span>
            </div>
            <button onClick={() => setActionSuccess(null)} className="text-emerald-500 hover:text-emerald-300">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {error && (
          <div className="flex items-center justify-between p-4 bg-red-950/40 border border-red-900/50 rounded text-red-400 text-sm">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span className="font-medium">{error}</span>
            </div>
            <button onClick={() => setError(null)} className="text-red-500 hover:text-red-300">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Active Deployments Table */}
        <div className="bg-slate-950 border border-slate-800 rounded overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-800 bg-slate-900/50">
            <h2 className="text-xs font-bold text-slate-300 uppercase tracking-widest">Active Operational Contexts</h2>
          </div>
          
          {loading ? (
            <div className="p-8 text-center text-slate-500 text-sm font-medium">Loading active deployments...</div>
          ) : operations.length === 0 ? (
            <div className="p-8 text-center text-slate-500 text-sm font-medium">No active temporary deployments found.</div>
          ) : (
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="p-4">Operation ID / Name</th>
                  <th className="p-4">Unit Assigned</th>
                  <th className="p-4">Zone & Duty</th>
                  <th className="p-4">Start Time</th>
                  <th className="p-4">Duration & Reversion</th>
                  <th className="p-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 text-slate-300">
                {operations.map((op) => (
                  <tr key={op.id} className="hover:bg-slate-900/60 transition-colors">
                    <td className="p-4">
                      <p className="font-bold text-white uppercase">{op.name}</p>
                      <p className="text-[10px] text-slate-500 font-mono mt-0.5">{op.id}</p>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2 font-medium">
                        <Shield className="w-3.5 h-3.5 text-slate-500" />
                        <span className="text-slate-200">{op.unit_id || 'Multiple'}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <p className="font-semibold text-slate-300">{op.zone}</p>
                      <p className="text-[11px] text-slate-500 mt-0.5">{op.duty_type} · {op.shift}</p>
                    </td>
                    <td className="p-4 text-slate-400">
                      {new Date(op.start_time).toLocaleDateString()} {new Date(op.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        {op.auto_revert && (
                          <span className="flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider bg-amber-950/60 text-amber-500 border border-amber-900">
                            <Timer className="w-3 h-3" />
                            Auto-Revert
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="p-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-emerald-950/60 text-emerald-400 border border-emerald-900">
                        Active
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Modal: Bulk Operational Assignment */}
        {showCreateModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
            <div className="w-full max-w-2xl bg-slate-900 border border-slate-700 rounded shadow-2xl overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-800 bg-slate-950 flex justify-between items-center">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Execute Command Operation</h3>
                <button onClick={() => setShowCreateModal(false)} className="text-slate-500 hover:text-white transition">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleCreateAssignment} className="p-6 space-y-6 text-sm">
                
                {/* 1. Operation Identity */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Operation Designation</label>
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full p-2.5 bg-slate-950 border border-slate-700 rounded text-slate-200 focus:outline-none focus:border-slate-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Target Unit</label>
                    <select
                      value={targetUnit}
                      onChange={(e) => setTargetUnit(e.target.value)}
                      className="w-full p-2.5 bg-slate-950 border border-slate-700 rounded text-slate-200 focus:outline-none focus:border-slate-500"
                    >
                      {units.map((u) => (
                        <option key={u.id} value={u.id}>{u.name} ({u.id})</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* 2. Tactical Context */}
                <div className="grid grid-cols-3 gap-4 p-4 border border-slate-800 rounded bg-slate-950/50">
                  <div>
                    <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">Operational Zone</label>
                    <select
                      value={zone}
                      onChange={(e) => setZone(e.target.value)}
                      className="w-full p-2 bg-slate-900 border border-slate-700 rounded text-slate-300 focus:outline-none"
                    >
                      <option value="Zone 1">Zone 1 (Base)</option>
                      <option value="Zone 2">Zone 2 (Forward)</option>
                      <option value="Zone 3">Zone 3 (Active)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">Duty Type</label>
                    <select
                      value={dutyType}
                      onChange={(e) => setDutyType(e.target.value)}
                      className="w-full p-2 bg-slate-900 border border-slate-700 rounded text-slate-300 focus:outline-none"
                      required
                    >
                      <option value="Border Patrol">Border Patrol</option>
                      <option value="Static Guard">Static Guard</option>
                      <option value="Reconnaissance">Reconnaissance</option>
                      <option value="Base Administration">Base Administration</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">Shift Block</label>
                    <select
                      value={shift}
                      onChange={(e) => setShift(e.target.value)}
                      className="w-full p-2 bg-slate-900 border border-slate-700 rounded text-slate-300 focus:outline-none"
                    >
                      <option value="Day (08:00 - 16:00)">Day (08:00 - 16:00)</option>
                      <option value="Evening (16:00 - 00:00)">Evening (16:00 - 00:00)</option>
                      <option value="Night (20:00 - 04:00)">Night (20:00 - 04:00)</option>
                      <option value="Irregular (Dynamic)">Irregular (Dynamic)</option>
                    </select>
                  </div>
                </div>

                {/* 3. Duration & Reversion */}
                <div className="flex gap-4 items-end bg-amber-950/20 border border-amber-900/30 p-4 rounded">
                  <div className="flex-1">
                    <label className="block text-xs font-bold text-amber-500 uppercase tracking-wider mb-2">Duration (Days)</label>
                    <input
                      type="number"
                      min="1"
                      max="90"
                      value={durationDays}
                      onChange={(e) => setDurationDays(Number(e.target.value))}
                      className="w-full p-2.5 bg-slate-950 border border-slate-700 rounded text-slate-200 font-mono focus:outline-none"
                      required
                    />
                  </div>
                  <div className="flex-1 pb-2">
                    <label className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={autoRevert}
                        onChange={(e) => setAutoRevert(e.target.checked)}
                        className="w-5 h-5 rounded border-slate-700 text-amber-500 focus:ring-0 bg-slate-950"
                      />
                      <div>
                        <span className="block text-xs font-bold text-amber-500 uppercase tracking-wider">Enable Auto-Revert</span>
                        <span className="block text-[10px] text-slate-400 mt-0.5">Personnel baseline returns to normal after duration</span>
                      </div>
                    </label>
                  </div>
                </div>

                {/* Actions */}
                <div className="pt-4 border-t border-slate-800 flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 rounded text-xs font-bold text-slate-400 hover:text-white uppercase tracking-wider transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-6 py-2 bg-slate-200 hover:bg-white text-slate-900 rounded text-xs font-bold uppercase tracking-wider transition shadow-sm disabled:opacity-50"
                  >
                    {submitting ? 'Executing...' : 'Execute Operation'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
}
