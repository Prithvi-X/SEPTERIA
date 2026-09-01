'use client';

import React, { useEffect, useState } from 'react';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { useAuth } from '@/lib/auth';
import { api, PersonnelItem, PersonnelDetail, UnitItem } from '@/lib/api';
import {
  Users, Search, Filter, MapPin, X, ChevronRight, Shield, CheckSquare, Square, AlertCircle, Plus, Clock, Activity, Flag, CheckCircle2
} from 'lucide-react';

export default function PersonnelPage() {
  const { user } = useAuth();
  const [personnel, setPersonnel] = useState<PersonnelItem[]>([]);
  const [units, setUnits] = useState<UnitItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Search
  const [search, setSearch] = useState('');
  const [selectedForce, setSelectedForce] = useState('');
  const [selectedUnit, setSelectedUnit] = useState('');
  const [selectedZone, setSelectedZone] = useState('');
  const [selectedLeaveStatus, setSelectedLeaveStatus] = useState('');

  // Multi-Selection
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  // Profile Drawer State
  const [selectedPersonnelId, setSelectedPersonnelId] = useState<string | null>(null);
  const [profileDetail, setProfileDetail] = useState<PersonnelDetail | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [showTechnical, setShowTechnical] = useState(false);

  const fetchUnits = async () => {
    try {
      const uList = await api.getUnits();
      setUnits(uList);
    } catch {}
  };

  const fetchPersonnel = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getPersonnel({
        skip: 0,
        limit: 100,
        force: selectedForce || undefined,
        unit_id: selectedUnit || undefined,
        current_zone: selectedZone || undefined,
        search: search || undefined,
        leave_status: selectedLeaveStatus || undefined
      });
      setPersonnel(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load personnel directory.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUnits();
  }, []);

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      fetchPersonnel();
    }, 400);
    return () => clearTimeout(delayDebounce);
  }, [search, selectedForce, selectedUnit, selectedZone, selectedLeaveStatus]);

  const loadProfile = async (id: string) => {
    setSelectedPersonnelId(id);
    setProfileLoading(true);
    setShowTechnical(false);
    try {
      const data = await api.getPersonnelDetail(id);
      setProfileDetail(data);
    } catch (err) {
      console.error(err);
    } finally {
      setProfileLoading(false);
    }
  };

  const closeProfile = () => {
    setSelectedPersonnelId(null);
    setProfileDetail(null);
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === personnel.length && personnel.length > 0) {
      setSelectedIds([]);
    } else {
      setSelectedIds(personnel.map(p => p.personnel_id));
    }
  };

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  return (
    <ProtectedRoute allowedRoles={['commander', 'welfare_officer', 'medical_officer', 'admin']}>
      <div className="flex h-[calc(100vh-4rem)] bg-slate-900 overflow-hidden relative">
        
        {/* Main Directory Area */}
        <div className={`flex-1 flex flex-col transition-all duration-300 ${selectedPersonnelId ? 'mr-96' : ''}`}>
          
          <div className="p-6 border-b border-slate-800 bg-slate-900/50">
            <h1 className="text-lg font-bold text-white tracking-tight uppercase">Personnel Directory</h1>
            <p className="text-xs text-slate-400 mt-1">
              Select personnel to view official records or perform bulk operational assignments.
            </p>

            <div className="mt-6 flex flex-wrap items-center gap-3">
              <div className="relative flex-1 min-w-[200px] max-w-sm">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search ID, name, or unit..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 text-sm text-slate-200 rounded px-9 py-2 focus:outline-none focus:border-slate-500 transition-colors"
                />
              </div>

              <select
                value={selectedUnit}
                onChange={(e) => setSelectedUnit(e.target.value)}
                className="bg-slate-950 border border-slate-700 text-sm text-slate-300 rounded px-3 py-2 focus:outline-none focus:border-slate-500"
              >
                <option value="">All Units</option>
                {units.map(u => (
                  <option key={u.id} value={u.id}>{u.name}</option>
                ))}
              </select>

              <select
                value={selectedZone}
                onChange={(e) => setSelectedZone(e.target.value)}
                className="bg-slate-950 border border-slate-700 text-sm text-slate-300 rounded px-3 py-2 focus:outline-none focus:border-slate-500"
              >
                <option value="">All Zones</option>
                <option value="Zone 1">Zone 1</option>
                <option value="Zone 2">Zone 2</option>
                <option value="Zone 3">Zone 3</option>
              </select>

              <select
                value={selectedLeaveStatus}
                onChange={(e) => setSelectedLeaveStatus(e.target.value)}
                className="bg-slate-950 border border-slate-700 text-sm text-slate-300 rounded px-3 py-2 focus:outline-none focus:border-slate-500"
              >
                <option value="">All Leave Status</option>
                <option value="ACTIVE_DUTY">Active Duty</option>
                <option value="POST_LEAVE_TRANSITION">Post-Leave Transition</option>
                <option value="ON_LEAVE">On Leave</option>
              </select>
            </div>
          </div>

          <div className="flex-1 overflow-auto p-6">
            {error ? (
              <div className="p-4 bg-red-950/40 border border-red-900/50 rounded text-red-400 text-sm flex items-center gap-3">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <p>{error}</p>
              </div>
            ) : (
              <div className="bg-slate-950 border border-slate-800 rounded overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                    <tr>
                      <th className="p-3 w-10 text-center border-r border-slate-800">
                        <button onClick={toggleSelectAll} className="text-slate-400 hover:text-white transition">
                          {selectedIds.length === personnel.length && personnel.length > 0 ? (
                            <CheckSquare className="w-4 h-4 text-slate-300" />
                          ) : (
                            <Square className="w-4 h-4" />
                          )}
                        </button>
                      </th>
                      <th className="p-3">Personnel</th>
                      <th className="p-3">Unit</th>
                      <th className="p-3">Current Duty</th>
                      <th className="p-3">Assignment Status</th>
                      <th className="p-3">Welfare State</th>
                      <th className="p-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 text-slate-300">
                    {loading ? (
                      <tr>
                        <td colSpan={7} className="p-8 text-center text-slate-500 font-medium">
                          Loading personnel directory...
                        </td>
                      </tr>
                    ) : personnel.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="p-8 text-center text-slate-500 font-medium">
                          No personnel matched the specified filter criteria.
                        </td>
                      </tr>
                    ) : (
                      personnel.map((p) => {
                        const isSelected = selectedIds.includes(p.personnel_id);
                        return (
                          <tr key={p.id} className="hover:bg-slate-900/60 transition-colors group">
                            <td className="p-3 text-center border-r border-slate-800/50">
                              <button onClick={() => toggleSelect(p.personnel_id)}>
                                {isSelected ? (
                                  <CheckSquare className="w-4 h-4 text-slate-300" />
                                ) : (
                                  <Square className="w-4 h-4 text-slate-600 group-hover:text-slate-400 transition-colors" />
                                )}
                              </button>
                            </td>
                            <td className="p-3">
                              <p className="font-bold text-white">{p.personnel_id}</p>
                              <p className="text-[11px] text-slate-500">{p.rank} • {p.role}</p>
                            </td>
                            <td className="p-3 font-medium text-slate-400">
                              {p.force} · {p.id}
                            </td>
                            <td className="p-3">
                              <p className="text-slate-200">{p.current_duty || 'Unassigned'}</p>
                              <p className="text-[11px] text-slate-500">{p.current_zone || 'Unknown Zone'} · {p.current_shift}</p>
                            </td>
                            <td className="p-3">
                              {p.leave_status === 'POST_LEAVE_TRANSITION' ? (
                                <span className="text-blue-400 font-medium">Post-Leave</span>
                              ) : p.active_context_id ? (
                                <span className="text-amber-400 font-medium">Temporary Deployment</span>
                              ) : (
                                <span className="text-slate-400 font-medium">Routine</span>
                              )}
                            </td>
                            <td className="p-3">
                              {p.status === 'HIGH' ? (
                                <span className="text-amber-500 font-semibold flex items-center gap-1">
                                  <AlertCircle className="w-3.5 h-3.5" />
                                  Attention Required
                                </span>
                              ) : (
                                <span className="text-emerald-500 font-semibold flex items-center gap-1">
                                  <CheckCircle2 className="w-3.5 h-3.5" />
                                  Stable
                                </span>
                              )}
                            </td>
                            <td className="p-3 text-right">
                              <button
                                onClick={() => loadProfile(p.personnel_id)}
                                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-medium rounded transition"
                              >
                                View Record
                              </button>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Profile Drawer */}
        <div
          className={`absolute top-0 right-0 w-96 h-full bg-slate-950 border-l border-slate-800 shadow-2xl transition-transform duration-300 ease-in-out ${
            selectedPersonnelId ? 'translate-x-0' : 'translate-x-full'
          } flex flex-col z-20`}
        >
          {profileLoading ? (
            <div className="flex-1 flex items-center justify-center text-slate-500 text-sm font-medium">
              Loading official record...
            </div>
          ) : profileDetail ? (
            <>
              {/* Drawer Header */}
              <div className="p-5 border-b border-slate-800 bg-slate-900 flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-bold text-white tracking-tight">{profileDetail.personnel_id}</h2>
                  <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mt-1">
                    {profileDetail.rank} • {profileDetail.force}
                  </p>
                </div>
                <button
                  onClick={closeProfile}
                  className="p-1.5 text-slate-500 hover:text-white rounded bg-slate-800/50 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Drawer Content */}
              <div className="flex-1 overflow-y-auto p-5 space-y-6">
                
                {/* Current Assignment */}
                <div>
                  <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">
                    Current Assignment
                  </h3>
                  <div className="bg-slate-900 border border-slate-800 rounded p-4 space-y-3">
                    <div className="flex items-start gap-3">
                      <MapPin className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                      <div>
                        <p className="text-sm font-semibold text-slate-200">{profileDetail.current_zone}</p>
                        <p className="text-xs text-slate-400 mt-0.5">{profileDetail.current_duty} • {profileDetail.current_shift}</p>
                      </div>
                    </div>
                    {profileDetail.active_context_id && (
                      <div className="pt-3 border-t border-slate-800">
                        <div className="flex items-center gap-2 text-amber-500 text-xs font-bold uppercase tracking-wider">
                          <Clock className="w-3.5 h-3.5" />
                          <span>Temporary Deployment</span>
                        </div>
                        <p className="text-[10px] font-bold text-slate-500 mt-1.5">AUTO-REVERT ENABLED</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Post-Leave Status */}
                <div>
                  <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">
                    Leave & Transition Status
                  </h3>
                  <div className="bg-slate-900 border border-slate-800 rounded p-4">
                    {profileDetail.leave_status === 'POST_LEAVE_TRANSITION' ? (
                      <div className="flex items-start gap-3">
                        <Activity className="w-4 h-4 text-blue-400 mt-0.5 shrink-0" />
                        <div>
                          <p className="text-sm font-semibold text-blue-400">Post-Leave Transition Active</p>
                          <p className="text-xs text-slate-400 mt-1">Day {profileDetail.post_leave_day_count || 1} of 14 reintegration protocol.</p>
                        </div>
                      </div>
                    ) : profileDetail.leave_status === 'ON_LEAVE' ? (
                      <div className="flex items-start gap-3">
                        <Flag className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                        <div>
                          <p className="text-sm font-semibold text-slate-300">Currently on Leave</p>
                        </div>
                      </div>
                    ) : (
                      <p className="text-xs font-medium text-slate-500">No active transition.</p>
                    )}
                  </div>
                </div>

                {/* Welfare Status (Authorized roles) */}
                {(user?.role === 'commander' || user?.role === 'medical_officer' || user?.role === 'welfare_officer') && (
                  <div>
                    <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">
                      Welfare State
                    </h3>
                    <div className="bg-slate-900 border border-slate-800 rounded p-4 space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium text-slate-400">Physiological Signal</span>
                        {profileDetail.status === 'HIGH' ? (
                          <span className="text-amber-500 font-bold text-xs uppercase tracking-wider">Attention Required</span>
                        ) : (
                          <span className="text-emerald-500 font-bold text-xs uppercase tracking-wider">Stable</span>
                        )}
                      </div>

                      <div className="pt-3 border-t border-slate-800">
                        <button
                          onClick={() => setShowTechnical(!showTechnical)}
                          className="text-[10px] font-bold text-slate-500 hover:text-slate-300 transition uppercase tracking-widest flex items-center gap-1"
                        >
                          <ChevronRight className={`w-3 h-3 transition-transform ${showTechnical ? 'rotate-90' : ''}`} />
                          Technical Evidence
                        </button>
                        
                        {showTechnical && (
                          <div className="mt-3 p-3 bg-slate-950 border border-slate-800 rounded space-y-2 text-xs text-slate-400 font-mono">
                            <div className="flex justify-between">
                              <span>Model Score:</span>
                              <span className="text-slate-300">{'78.5%'}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Heart Rate Base:</span>
                              <span className="text-slate-300">{'N/A'}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>HRV Index:</span>
                              <span className="text-slate-300">{'N/A'}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Sleep Ratio:</span>
                              <span className="text-slate-300">{'N/A'}</span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : null}
        </div>
      </div>
    </ProtectedRoute>
  );
}
