'use client';

import React, { useEffect, useState } from 'react';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { useAuth } from '@/lib/auth';
import { api, PersonnelItem, PersonnelDetail, UnitItem } from '@/lib/api';
import {
  Users,
  Search,
  Filter,
  Layers,
  Clock,
  MapPin,
  Calendar,
  X,
  ChevronRight,
  TrendingUp,
  Shield,
  CheckSquare,
  Square,
  AlertCircle,
  CheckCircle2,
  Plus
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
  const [selectedStatus, setSelectedStatus] = useState('');
  const [selectedLeaveStatus, setSelectedLeaveStatus] = useState('');

  // Multi-Selection
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  // Profile Drawer State
  const [selectedPersonnelId, setSelectedPersonnelId] = useState<string | null>(null);
  const [profileDetail, setProfileDetail] = useState<PersonnelDetail | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);

  // Leave Return Modal State
  const [showLeaveModal, setShowLeaveModal] = useState(false);
  const [leaveType, setLeaveType] = useState('ANNUAL_LEAVE');
  const [leaveEndDate, setLeaveEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [returnDate, setReturnDate] = useState(new Date().toISOString().split('T')[0]);
  const [leaveSubmitting, setLeaveSubmitting] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Bulk Assign Modal Redirect / State
  const [showBulkModal, setShowBulkModal] = useState(false);
  const [bulkAssignmentName, setBulkAssignmentName] = useState('Forward Sector Tactical Duty');
  const [bulkZone, setBulkZone] = useState('Zone 2');
  const [bulkDuty, setBulkDuty] = useState('Border Patrol');
  const [bulkShift, setBulkShift] = useState('Night (20:00 - 04:00)');
  const [bulkLocation, setBulkLocation] = useState('Sector Forward Line B');
  const [bulkEnvironment, setBulkEnvironment] = useState('High Heat / Extreme Arid');
  const [bulkDays, setBulkDays] = useState(7);
  const [bulkAutoRevert, setBulkAutoRevert] = useState(true);
  const [bulkSubmitting, setBulkSubmitting] = useState(false);

  const fetchUnits = async () => {
    try {
      const uList = await api.getUnits();
      setUnits(uList);
    } catch {
      // Ignore
    }
  };

  const fetchPersonnel = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getPersonnel({
        search,
        force: selectedForce || undefined,
        unit_id: selectedUnit || undefined,
        zone: selectedZone || undefined,
        status: selectedStatus || undefined,
        leave_status: selectedLeaveStatus || undefined,
      });
      setPersonnel(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load personnel records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUnits();
  }, []);

  useEffect(() => {
    fetchPersonnel();
  }, [search, selectedForce, selectedUnit, selectedZone, selectedStatus, selectedLeaveStatus]);

  const openProfile = async (id: string) => {
    try {
      setSelectedPersonnelId(id);
      setProfileLoading(true);
      const detail = await api.getPersonnelDetail(id);
      setProfileDetail(detail);
    } catch (err: any) {
      setError(err.message || 'Failed to load profile details.');
    } finally {
      setProfileLoading(false);
    }
  };

  const closeProfile = () => {
    setSelectedPersonnelId(null);
    setProfileDetail(null);
    setActionSuccess(null);
  };

  // Toggle single selection
  const toggleSelect = (pid: string) => {
    setSelectedIds((prev) =>
      prev.includes(pid) ? prev.filter((id) => id !== pid) : [...prev, pid]
    );
  };

  // Toggle all visible selection
  const toggleSelectAll = () => {
    if (selectedIds.length === personnel.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(personnel.map((p) => p.personnel_id));
    }
  };

  // Submit Leave Return
  const handleLeaveReturnSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profileDetail) return;
    setLeaveSubmitting(true);
    setError(null);
    try {
      const res = await api.recordLeaveReturn(profileDetail.personnel_id, {
        leave_type: leaveType,
        leave_end_date: new Date(leaveEndDate).toISOString(),
        return_date: new Date(returnDate).toISOString(),
      });
      setActionSuccess(res.message);
      setShowLeaveModal(false);
      // Refresh profile and list
      openProfile(profileDetail.personnel_id);
      fetchPersonnel();
    } catch (err: any) {
      setError(err.message || 'Failed to record return from leave.');
    } finally {
      setLeaveSubmitting(false);
    }
  };

  // Submit Bulk Assignment for Selected Personnel
  const handleBulkAssignSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBulkSubmitting(true);
    setError(null);
    try {
      const res = await api.bulkAssign({
        assignment_name: bulkAssignmentName,
        personnel_ids: selectedIds.length > 0 ? selectedIds : undefined,
        unit_id: selectedIds.length === 0 && selectedUnit ? selectedUnit : undefined,
        zone: bulkZone,
        duty_type: bulkDuty,
        shift: bulkShift,
        location: bulkLocation,
        environment: bulkEnvironment,
        duration_days: Number(bulkDays),
        auto_revert: bulkAutoRevert,
      });

      setActionSuccess(res.message);
      setShowBulkModal(false);
      setSelectedIds([]);
      fetchPersonnel();
    } catch (err: any) {
      setError(err.message || 'Failed to apply bulk assignment.');
    } finally {
      setBulkSubmitting(false);
    }
  };

  const isCommanderOrAdmin = user?.role === 'commander' || user?.role === 'admin';
  const isWelfareOrCommander = user?.role === 'welfare_officer' || user?.role === 'commander' || user?.role === 'admin';

  return (
    <ProtectedRoute allowedRoles={['commander', 'welfare_officer', 'medical_officer', 'admin']}>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-5">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">Personnel Directory & Roster</h1>
            <p className="text-xs text-slate-400 mt-1">
              Authoritative personnel records, current operational postings, and leave transition status
            </p>
          </div>
          {isCommanderOrAdmin && (
            <button
              onClick={() => setShowBulkModal(true)}
              className="flex items-center gap-2 px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium transition shadow-sm"
            >
              <Plus className="w-4 h-4" />
              <span>Bulk Assign Context {selectedIds.length > 0 ? `(${selectedIds.length})` : ''}</span>
            </button>
          )}
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

        {/* Search & Filters */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">
          <div className="relative sm:col-span-2">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by ID, Rank, Force (e.g. BSF-47001)..."
              className="w-full pl-10 pr-4 py-2 bg-slate-950/80 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <select
            value={selectedUnit}
            onChange={(e) => setSelectedUnit(e.target.value)}
            className="px-3 py-2 bg-slate-950/80 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Units / Battalions</option>
            {units.map((u) => (
              <option key={u.id} value={u.code}>
                {u.code} ({u.personnel_count} Jawans)
              </option>
            ))}
          </select>

          <select
            value={selectedForce}
            onChange={(e) => setSelectedForce(e.target.value)}
            className="px-3 py-2 bg-slate-950/80 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Forces</option>
            <option value="BSF">BSF</option>
            <option value="CRPF">CRPF</option>
            <option value="ITBP">ITBP</option>
            <option value="CISF">CISF</option>
          </select>

          <select
            value={selectedZone}
            onChange={(e) => setSelectedZone(e.target.value)}
            className="px-3 py-2 bg-slate-950/80 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Operational Zones</option>
            <option value="Zone 1">Zone 1 (Active Ops)</option>
            <option value="Zone 2">Zone 2 (Border / Extreme)</option>
            <option value="Zone 3">Zone 3 (Incident Recovery)</option>
          </select>

          <select
            value={selectedLeaveStatus}
            onChange={(e) => setSelectedLeaveStatus(e.target.value)}
            className="px-3 py-2 bg-slate-950/80 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Leave States</option>
            <option value="POST_LEAVE_TRANSITION">Post-Leave Transition (14-Day)</option>
            <option value="NONE">Active Duty (No Transition)</option>
          </select>
        </div>

        {/* Selected Items Multi-Action Banner */}
        {selectedIds.length > 0 && (
          <div className="flex items-center justify-between p-3 bg-blue-950/40 border border-blue-800/80 rounded-xl text-xs">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded bg-blue-600 text-white font-bold font-mono">
                {selectedIds.length}
              </span>
              <span className="text-slate-200 font-medium">Personnel Selected for Batch Action</span>
            </div>
            <div className="flex items-center gap-2">
              {isCommanderOrAdmin ? (
                <button
                  onClick={() => setShowBulkModal(true)}
                  className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg transition"
                >
                  Apply Operational Context to Selected ({selectedIds.length})
                </button>
              ) : (
                <span className="text-slate-400 italic">Read-only role: Cannot apply tactical batch assignments</span>
              )}
              <button
                onClick={() => setSelectedIds([])}
                className="px-2.5 py-1.5 text-slate-400 hover:text-slate-200"
              >
                Clear
              </button>
            </div>
          </div>
        )}

        {/* Personnel Directory Data Table */}
        <div className="bg-slate-950/60 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="p-3.5 w-10 text-center">
                    <button onClick={toggleSelectAll} className="text-slate-400 hover:text-white">
                      {selectedIds.length === personnel.length && personnel.length > 0 ? (
                        <CheckSquare className="w-4 h-4 text-blue-400" />
                      ) : (
                        <Square className="w-4 h-4" />
                      )}
                    </button>
                  </th>
                  <th className="p-3.5">Personnel ID</th>
                  <th className="p-3.5">Force / Unit</th>
                  <th className="p-3.5">Rank & Role</th>
                  <th className="p-3.5">Operational Zone</th>
                  <th className="p-3.5">Current Duty & Shift</th>
                  <th className="p-3.5">Deployment / Status</th>
                  <th className="p-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="p-8 text-center text-slate-500">
                      <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                      Loading personnel directory from PostgreSQL 16...
                    </td>
                  </tr>
                ) : personnel.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="p-8 text-center text-slate-500">
                      No personnel matched the specified filter criteria.
                    </td>
                  </tr>
                ) : (
                  personnel.map((p) => {
                    const isSelected = selectedIds.includes(p.personnel_id);
                    return (
                      <tr
                        key={p.id}
                        className={`hover:bg-slate-900/50 transition cursor-pointer ${
                          isSelected ? 'bg-blue-950/20' : ''
                        }`}
                        onClick={() => openProfile(p.personnel_id)}
                      >
                        <td
                          className="p-3.5 text-center"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleSelect(p.personnel_id);
                          }}
                        >
                          {isSelected ? (
                            <CheckSquare className="w-4 h-4 text-blue-400 mx-auto" />
                          ) : (
                            <Square className="w-4 h-4 text-slate-600 mx-auto" />
                          )}
                        </td>
                        <td className="p-3.5 font-mono font-semibold text-white">
                          {p.personnel_id}
                        </td>
                        <td className="p-3.5">
                          <span className="font-medium text-slate-200">{p.force}</span>
                          <span className="block text-[11px] text-slate-500 font-mono">{p.unit_id}</span>
                        </td>
                        <td className="p-3.5">
                          <span className="font-medium text-slate-200">{p.rank}</span>
                          <span className="block text-[11px] text-slate-500">{p.posting}</span>
                        </td>
                        <td className="p-3.5">
                          <span
                            className={`inline-block px-2.5 py-0.5 rounded text-[11px] font-semibold border ${
                              p.current_zone.includes('1')
                                ? 'bg-red-950/60 text-red-300 border-red-800/40'
                                : p.current_zone.includes('2')
                                ? 'bg-amber-950/60 text-amber-300 border-amber-800/40'
                                : 'bg-purple-950/60 text-purple-300 border-purple-800/40'
                            }`}
                          >
                            {p.current_zone}
                          </span>
                        </td>
                        <td className="p-3.5">
                          <span className="text-slate-200 font-medium">{p.current_duty}</span>
                          <span className="block text-[11px] text-slate-500">{p.current_shift}</span>
                        </td>
                        <td className="p-3.5">
                          {p.is_temporary_deployment ? (
                            <div className="flex items-center gap-1.5 text-purple-300">
                              <Clock className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
                              <span className="text-[11px] font-mono font-medium">
                                {p.remaining_duration_formatted || 'Temporary'}
                              </span>
                            </div>
                          ) : p.leave_status === 'POST_LEAVE_TRANSITION' ? (
                            <div className="flex items-center gap-1.5 text-amber-300">
                              <TrendingUp className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
                              <span className="text-[11px] font-medium">
                                Transition: Day {p.post_leave_day_count || 1} / 14
                              </span>
                            </div>
                          ) : (
                            <span className="inline-block px-2 py-0.5 rounded bg-slate-900 text-slate-400 text-[11px]">
                              Standard Active
                            </span>
                          )}
                        </td>
                        <td className="p-3.5 text-right">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              openProfile(p.personnel_id);
                            }}
                            className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 text-[11px] font-medium border border-slate-800 transition"
                          >
                            <span>Profile</span>
                            <ChevronRight className="w-3 h-3" />
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Profile Inspector Drawer */}
        {selectedPersonnelId && (
          <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm">
            <div className="w-full max-w-lg bg-slate-950 border-l border-slate-800 p-6 overflow-y-auto space-y-6 shadow-2xl animate-in slide-in-from-right duration-200">
              {/* Drawer Header */}
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <h2 className="text-lg font-bold text-white tracking-tight">
                    {profileDetail ? profileDetail.personnel_id : 'Loading...'}
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Administrative Personnel Profile • SIH26186
                  </p>
                </div>
                <button
                  onClick={closeProfile}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 transition"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {profileLoading || !profileDetail ? (
                <div className="p-8 text-center text-slate-500">
                  <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                  Loading profile context...
                </div>
              ) : (
                <>
                  {/* Personnel Info Box */}
                  <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-3">
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <span className="text-slate-500">Force / Organization</span>
                        <p className="font-semibold text-slate-200 mt-0.5">{profileDetail.force}</p>
                      </div>
                      <div>
                        <span className="text-slate-500">Unit / Battalion</span>
                        <p className="font-semibold text-slate-200 mt-0.5">{profileDetail.unit_id}</p>
                      </div>
                      <div>
                        <span className="text-slate-500">Rank / Designation</span>
                        <p className="font-semibold text-slate-200 mt-0.5">{profileDetail.rank}</p>
                      </div>
                      <div>
                        <span className="text-slate-500">Permanent Posting</span>
                        <p className="font-semibold text-slate-200 mt-0.5">{profileDetail.posting}</p>
                      </div>
                    </div>
                  </div>

                  {/* Active Operational Context Box */}
                  <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Layers className="w-4 h-4 text-blue-400" />
                        <h3 className="text-xs font-semibold text-white uppercase tracking-wider">
                          Current Operational Context
                        </h3>
                      </div>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                          profileDetail.current_zone.includes('1')
                            ? 'bg-red-950 text-red-300 border-red-800'
                            : profileDetail.current_zone.includes('2')
                            ? 'bg-amber-950 text-amber-300 border-amber-800'
                            : 'bg-purple-950 text-purple-300 border-purple-800'
                        }`}
                      >
                        {profileDetail.current_zone}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs pt-1">
                      <div>
                        <span className="text-slate-500">Duty Assignment</span>
                        <p className="font-semibold text-slate-200 mt-0.5">{profileDetail.current_duty}</p>
                      </div>
                      <div>
                        <span className="text-slate-500">Duty Shift</span>
                        <p className="font-semibold text-slate-200 mt-0.5">{profileDetail.current_shift}</p>
                      </div>
                      <div>
                        <span className="text-slate-500">Active Location</span>
                        <p className="font-semibold text-slate-200 mt-0.5">{profileDetail.current_location}</p>
                      </div>
                      <div>
                        <span className="text-slate-500">Environment</span>
                        <p className="font-semibold text-slate-200 mt-0.5">{profileDetail.current_environment}</p>
                      </div>
                    </div>

                    {profileDetail.is_temporary_deployment && (
                      <div className="mt-3 p-3 bg-purple-950/30 border border-purple-900/60 rounded-lg flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2 text-purple-300">
                          <Clock className="w-4 h-4 text-purple-400 flex-shrink-0 animate-pulse" />
                          <div>
                            <span className="font-semibold">Temporary Rotation Countdown</span>
                            <p className="text-[11px] text-purple-400/80 font-mono">
                              {profileDetail.remaining_duration_formatted}
                            </p>
                          </div>
                        </div>
                        <span className="px-2 py-0.5 rounded bg-purple-900/60 text-purple-200 text-[10px] uppercase font-semibold">
                          Auto-Revert ON
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Post-Leave Reintegration Card */}
                  <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-amber-400" />
                        <h3 className="text-xs font-semibold text-white uppercase tracking-wider">
                          Post-Leave Reintegration Status
                        </h3>
                      </div>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          profileDetail.leave_status === 'POST_LEAVE_TRANSITION'
                            ? 'bg-amber-950 text-amber-300 border border-amber-800'
                            : 'bg-slate-900 text-slate-400'
                        }`}
                      >
                        {profileDetail.leave_status === 'POST_LEAVE_TRANSITION'
                          ? `DAY ${profileDetail.post_leave_day_count || 1} / 14`
                          : 'ROUTINE DUTY'}
                      </span>
                    </div>

                    {profileDetail.leave_status === 'POST_LEAVE_TRANSITION' ? (
                      <div className="space-y-2">
                        <p className="text-xs text-slate-300">
                          Personnel is actively in the 14-day post-leave transition period. Operational context is monitored without clinical risk scoring.
                        </p>
                        <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                          <div
                            className="bg-amber-400 h-2 rounded-full transition-all"
                            style={{
                              width: `${((profileDetail.post_leave_day_count || 1) / 14) * 100}%`,
                            }}
                          ></div>
                        </div>
                      </div>
                    ) : (
                      <p className="text-xs text-slate-400">
                        No active post-leave reintegration period for this personnel.
                      </p>
                    )}

                    {isWelfareOrCommander && (
                      <button
                        onClick={() => setShowLeaveModal(true)}
                        className="w-full mt-2 py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 transition flex items-center justify-center gap-1.5"
                      >
                        <Calendar className="w-3.5 h-3.5 text-amber-400" />
                        <span>Record "Returned from Leave"</span>
                      </button>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* Modal: Record Leave Return */}
        {showLeaveModal && profileDetail && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div className="w-full max-w-md bg-slate-950 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-2xl animate-in zoom-in-95 duration-150">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2 text-amber-400">
                  <Calendar className="w-5 h-5" />
                  <h3 className="text-sm font-bold text-white">Record Return from Leave</h3>
                </div>
                <button onClick={() => setShowLeaveModal(false)} className="text-slate-400 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <p className="text-xs text-slate-400">
                Recording return activates the 14-day transition window for <strong>{profileDetail.personnel_id}</strong>.
              </p>

              <form onSubmit={handleLeaveReturnSubmit} className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Leave Type</label>
                  <select
                    value={leaveType}
                    onChange={(e) => setLeaveType(e.target.value)}
                    className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                  >
                    <option value="ANNUAL_LEAVE">Annual Leave</option>
                    <option value="CASUAL_LEAVE">Casual Leave</option>
                    <option value="MEDICAL_LEAVE">Medical Leave</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Leave End Date</label>
                  <input
                    type="date"
                    value={leaveEndDate}
                    onChange={(e) => setLeaveEndDate(e.target.value)}
                    className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                    required
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Actual Return Date</label>
                  <input
                    type="date"
                    value={returnDate}
                    onChange={(e) => setReturnDate(e.target.value)}
                    className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                    required
                  />
                </div>

                <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowLeaveModal(false)}
                    className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={leaveSubmitting}
                    className="px-4 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg font-medium transition disabled:opacity-50"
                  >
                    {leaveSubmitting ? 'Recording...' : 'Activate 14-Day Transition'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal: Bulk Operational Assignment */}
        {showBulkModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div className="w-full max-w-lg bg-slate-950 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-2xl animate-in zoom-in-95 duration-150">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2 text-blue-400">
                  <Layers className="w-5 h-5" />
                  <h3 className="text-sm font-bold text-white">Create Tactical Bulk Assignment</h3>
                </div>
                <button onClick={() => setShowBulkModal(false)} className="text-slate-400 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="p-3 bg-blue-950/40 border border-blue-900/60 rounded-lg text-xs text-blue-300">
                <strong>Target Batch:</strong>{' '}
                {selectedIds.length > 0 ? (
                  <span>{selectedIds.length} Selected Personnel from directory</span>
                ) : selectedUnit ? (
                  <span>All personnel in Battalion {selectedUnit}</span>
                ) : (
                  <span>All personnel in BSF-BN-47 (147 Personnel)</span>
                )}
              </div>

              <form onSubmit={handleBulkAssignSubmit} className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Assignment Name</label>
                  <input
                    type="text"
                    value={bulkAssignmentName}
                    onChange={(e) => setBulkAssignmentName(e.target.value)}
                    className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-400 mb-1">Operational Zone</label>
                    <select
                      value={bulkZone}
                      onChange={(e) => setBulkZone(e.target.value)}
                      className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                    >
                      <option value="Zone 1">Zone 1 (Active Operations / QRT)</option>
                      <option value="Zone 2">Zone 2 (Border / Extreme Env)</option>
                      <option value="Zone 3">Zone 3 (Post-Incident Recovery)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">Duty Type</label>
                    <input
                      type="text"
                      value={bulkDuty}
                      onChange={(e) => setBulkDuty(e.target.value)}
                      className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-400 mb-1">Shift</label>
                    <select
                      value={bulkShift}
                      onChange={(e) => setBulkShift(e.target.value)}
                      className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                    >
                      <option value="Night (20:00 - 04:00)">Night (20:00 - 04:00)</option>
                      <option value="Day (08:00 - 16:00)">Day (08:00 - 16:00)</option>
                      <option value="Rotational (12-hr)">Rotational (12-hr)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">Environment</label>
                    <select
                      value={bulkEnvironment}
                      onChange={(e) => setBulkEnvironment(e.target.value)}
                      className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                    >
                      <option value="High Heat / Extreme Arid">High Heat / Extreme Arid</option>
                      <option value="Extreme Cold / Low Oxygen">Extreme Cold / Low Oxygen</option>
                      <option value="High Humidity / Dense Forest">High Humidity / Dense Forest</option>
                      <option value="Standard Base Environment">Standard Base Environment</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Location / Sector</label>
                  <input
                    type="text"
                    value={bulkLocation}
                    onChange={(e) => setBulkLocation(e.target.value)}
                    className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-400 mb-1">Duration (Days)</label>
                    <input
                      type="number"
                      min={1}
                      max={90}
                      value={bulkDays}
                      onChange={(e) => setBulkDays(Number(e.target.value))}
                      className="w-full p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 font-mono"
                      required
                    />
                  </div>

                  <div className="flex items-center pt-6">
                    <label className="flex items-center gap-2 cursor-pointer text-slate-300">
                      <input
                        type="checkbox"
                        checked={bulkAutoRevert}
                        onChange={(e) => setBulkAutoRevert(e.target.checked)}
                        className="rounded border-slate-700 text-blue-600 focus:ring-0"
                      />
                      <span>Auto-Revert on Expiry</span>
                    </label>
                  </div>
                </div>

                <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowBulkModal(false)}
                    className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={bulkSubmitting}
                    className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition disabled:opacity-50"
                  >
                    {bulkSubmitting ? 'Applying to Database...' : 'Apply Operational Assignment'}
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
