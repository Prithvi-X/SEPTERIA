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
  Layers,
  CheckCircle2,
  AlertCircle,
  X,
  Shield,
  History,
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
    } catch (err: any) {
      setError(err.message || 'Failed to evaluate automatic reversions.');
    } finally {
      setReverting(false);
    }
  };

  const isCommanderOrAdmin = user?.role === 'commander' || user?.role === 'admin';

  return (
    <ProtectedRoute allowedRoles={['commander', 'welfare_officer', 'medical_officer', 'admin']}>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-5">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">Operational Context & Deployments</h1>
            <p className="text-xs text-slate-400 mt-1">
              Authoritative duty assignments, operational zones, and time-bound temporary deployments with auto-revert
            </p>
          </div>
          <div className="flex items-center gap-3">
            {isCommanderOrAdmin && (
              <button
                onClick={handleEvaluateReversions}
                disabled={reverting}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-lg text-xs font-medium border border-slate-700 transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${reverting ? 'animate-spin' : ''}`} />
                <span>Simulate Auto-Reversion</span>
              </button>
            )}
            {isCommanderOrAdmin ? (
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center gap-2 px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium transition shadow-sm"
              >
                <Plus className="w-4 h-4" />
                <span>Create Tactical Assignment</span>
              </button>
            ) : (
              <span className="text-xs text-slate-400 italic">Read-Only View</span>
            )}
          </div>
        </div>

        {/* Global Notifications */}
        {actionSuccess && (
          <div className="flex items-center justify-between p-3.5 bg-emerald-950/60 border border-emerald-800/80 rounded-xl text-emerald-300 text-xs">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span>{actionSuccess}</span>
            </div>
            <button onClick={() => setActionSuccess(null)} className="text-emerald-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {error && (
          <div className="flex items-center justify-between p-3.5 bg-red-950/40 border border-red-800/60 rounded-xl text-red-300 text-xs">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
              <span>{error}</span>
            </div>
            <button onClick={() => setError(null)} className="text-red-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Operational Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl">
            <div className="flex items-center gap-2 text-purple-400 text-xs font-semibold">
              <Timer className="w-4 h-4" />
              <span>Dynamic Countdown</span>
            </div>
            <p className="text-xs text-slate-400 mt-2">
              Remaining time computed from PostgreSQL UTC timestamps (<code className="text-slate-300">end_time - now()</code>).
            </p>
          </div>

          <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl">
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold">
              <RefreshCw className="w-4 h-4" />
              <span>Deterministic Auto-Reversion</span>
            </div>
            <p className="text-xs text-slate-400 mt-2">
              Snapshots previous baseline upon assignment. When expired, baseline is restored with audit log.
            </p>
          </div>

          <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl">
            <div className="flex items-center gap-2 text-blue-400 text-xs font-semibold">
              <History className="w-4 h-4" />
              <span>Post-Leave Transition</span>
            </div>
            <p className="text-xs text-slate-400 mt-2">
              Leave returns trigger authoritative 14-day reintegration state without manual re-entry.
            </p>
          </div>

          <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl">
            <div className="flex items-center gap-2 text-cyan-400 text-xs font-semibold">
              <Shield className="w-4 h-4" />
              <span>Telemetry Ingestion & SQI</span>
            </div>
            <p className="text-xs text-slate-400 mt-2">
              Multimodal pipeline (94.8% sync) verifies SQI, tracks missingness, and preserves strict private RBAC.
            </p>
          </div>
        </div>

        {/* 3-Zone Operational Intelligence Summary */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-cyan-400" />
              <h2 className="text-xs font-bold text-white uppercase tracking-wider">3-Zone Operational Intelligence & Context Matrix</h2>
            </div>
            <span className="text-[11px] font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800 px-2 py-0.5 rounded">
              Phase 5 Engine Active
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-lg">
              <span className="text-slate-400 font-semibold block mb-1">Zone 1: Active Operations</span>
              <p className="text-[11px] text-slate-300">
                Focus: Acute cardiovascular load, physical exertion context, and immediate recovery opportunity.
              </p>
            </div>
            <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-lg">
              <span className="text-slate-400 font-semibold block mb-1">Zone 2: Border / Remote</span>
              <p className="text-[11px] text-slate-300">
                Focus: Multi-day HRV trajectories, cumulative sleep deficit, thermal/altitude strain, and deployment countdown.
              </p>
            </div>
            <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-lg">
              <span className="text-slate-400 font-semibold block mb-1">Zone 3: Critical Incident</span>
              <p className="text-[11px] text-slate-300">
                Focus: Post-event cardiovascular stabilization, recovery rebound detection, and autonomic return to baseline.
              </p>
            </div>
          </div>
        </div>

        {/* Active Deployments Table */}
        <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-400" />
              <h2 className="text-sm font-semibold text-white">Active & Historical Operational Deployments</h2>
            </div>
            <span className="text-xs text-slate-400 font-mono">
              {operations.length} Records in Database
            </span>
          </div>

          {loading ? (
            <div className="p-8 text-center text-slate-500">
              <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
              Loading operational contexts...
            </div>
          ) : operations.length === 0 ? (
            <div className="p-8 text-center text-slate-500">
              No operational assignments recorded. Create your first tactical assignment above.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                  <tr>
                    <th className="p-3">Assignment Name</th>
                    <th className="p-3">Target Unit / Jawan</th>
                    <th className="p-3">Zone</th>
                    <th className="p-3">Duty & Shift</th>
                    <th className="p-3">Location & Environment</th>
                    <th className="p-3">Remaining Duration</th>
                    <th className="p-3 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {operations.map((op) => (
                    <tr key={op.id} className="hover:bg-slate-900/40 transition">
                      <td className="p-3 font-semibold text-white">
                        {op.name || 'Tactical Operational Context'}
                        {op.notes && (
                          <span className="block text-[11px] text-slate-500 font-normal truncate max-w-xs">
                            {op.notes}
                          </span>
                        )}
                      </td>
                      <td className="p-3">
                        <span className="font-mono font-medium text-slate-200">
                          {op.personnel_id ? op.personnel_id : op.unit_id ? `Unit: ${op.unit_id}` : 'All Units'}
                        </span>
                      </td>
                      <td className="p-3">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold border ${
                            op.zone.includes('1')
                              ? 'bg-red-950/60 text-red-300 border-red-800/40'
                              : op.zone.includes('2')
                              ? 'bg-amber-950/60 text-amber-300 border-amber-800/40'
                              : 'bg-purple-950/60 text-purple-300 border-purple-800/40'
                          }`}
                        >
                          {op.zone}
                        </span>
                      </td>
                      <td className="p-3">
                        <span className="text-slate-200">{op.duty_type}</span>
                        <span className="block text-[11px] text-slate-500">{op.shift}</span>
                      </td>
                      <td className="p-3">
                        <span className="text-slate-200">{op.location}</span>
                        <span className="block text-[11px] text-slate-500">{op.environment}</span>
                      </td>
                      <td className="p-3">
                        {op.temporary && op.end_time ? (
                          <div className="flex items-center gap-1.5">
                            <Clock className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
                            <span className="font-mono text-purple-300 text-[11px]">
                              {op.remaining_duration_formatted || 'Active'}
                            </span>
                          </div>
                        ) : (
                          <span className="text-slate-500 text-[11px]">Permanent Baseline</span>
                        )}
                      </td>
                      <td className="p-3 text-right">
                        <span
                          className={`inline-block px-2.5 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${
                            op.status === 'ACTIVE'
                              ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800/60'
                              : op.status === 'REVERTED'
                              ? 'bg-slate-900 text-slate-400 border-slate-700'
                              : 'bg-amber-950/60 text-amber-300 border-amber-800/40'
                          }`}
                        >
                          {op.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Modal: Create Operational Assignment */}
        {showCreateModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div className="w-full max-w-lg bg-slate-950 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-2xl animate-in zoom-in-95 duration-150">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2 text-blue-400">
                  <Plus className="w-5 h-5" />
                  <h3 className="text-sm font-bold text-white">Create Operational Assignment</h3>
                </div>
                <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <form onSubmit={handleCreateAssignment} className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Assignment Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-400 mb-1">Target Unit</label>
                    <select
                      value={targetUnit}
                      onChange={(e) => setTargetUnit(e.target.value)}
                      className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                    >
                      {units.map((u) => (
                        <option key={u.id} value={u.code}>
                          {u.code} - {u.name} ({u.personnel_count} Jawans)
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">Operational Zone</label>
                    <select
                      value={zone}
                      onChange={(e) => setZone(e.target.value)}
                      className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                    >
                      <option value="Zone 1">Zone 1 (Active Operations / QRT)</option>
                      <option value="Zone 2">Zone 2 (Border / Extreme Env)</option>
                      <option value="Zone 3">Zone 3 (Post-Incident Recovery)</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-400 mb-1">Duty Type</label>
                    <input
                      type="text"
                      value={dutyType}
                      onChange={(e) => setDutyType(e.target.value)}
                      className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">Shift</label>
                    <select
                      value={shift}
                      onChange={(e) => setShift(e.target.value)}
                      className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                    >
                      <option value="Night (20:00 - 04:00)">Night (20:00 - 04:00)</option>
                      <option value="Day (08:00 - 16:00)">Day (08:00 - 16:00)</option>
                      <option value="Rotational (12-hr)">Rotational (12-hr)</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-400 mb-1">Location / Sector</label>
                    <input
                      type="text"
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">Environment</label>
                    <select
                      value={environment}
                      onChange={(e) => setEnvironment(e.target.value)}
                      className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                    >
                      <option value="High Heat / Desert Arid">High Heat / Desert Arid</option>
                      <option value="Extreme Cold / Low Oxygen">Extreme Cold / Low Oxygen</option>
                      <option value="High Humidity / Dense Forest">High Humidity / Dense Forest</option>
                      <option value="Standard Base Environment">Standard Base Environment</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-400 mb-1">Duration (Days)</label>
                    <input
                      type="number"
                      min={1}
                      max={90}
                      value={durationDays}
                      onChange={(e) => setDurationDays(Number(e.target.value))}
                      className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 font-mono"
                      required
                    />
                  </div>

                  <div className="flex items-center pt-6">
                    <label className="flex items-center gap-2 cursor-pointer text-slate-300">
                      <input
                        type="checkbox"
                        checked={autoRevert}
                        onChange={(e) => setAutoRevert(e.target.checked)}
                        className="rounded border-slate-700 text-blue-600 focus:ring-0"
                      />
                      <span>Auto-Revert upon Expiry</span>
                    </label>
                  </div>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Operational Notes / Reason</label>
                  <textarea
                    rows={2}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                  ></textarea>
                </div>

                <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition disabled:opacity-50"
                  >
                    {submitting ? 'Persisting Assignment...' : 'Commit Operational Deployment'}
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
