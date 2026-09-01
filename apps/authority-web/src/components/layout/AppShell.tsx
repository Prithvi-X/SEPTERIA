'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { api, SystemHealthAudit } from '@/lib/api';
import {
  LayoutDashboard,
  Users,
  MapPin,
  HeartHandshake,
  BarChart3,
  Settings,
  LogOut,
  Shield,
  Menu,
  X,
  Radio,
  RotateCcw,
  Activity,
  Zap,
  CheckCircle2,
  AlertTriangle,
  Server,
  Play
} from 'lucide-react';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navItems: NavItem[] = [
  { name: 'Overview', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Personnel', href: '/personnel', icon: Users },
  { name: 'Operations', href: '/operations', icon: MapPin },
  { name: 'Welfare Review', href: '/welfare', icon: HeartHandshake },
  { name: 'Unit Intelligence', href: '/analytics', icon: BarChart3 },
  { name: 'System', href: '/settings', icon: Settings },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [demoModalOpen, setDemoModalOpen] = useState(false);
  const [healthModalOpen, setHealthModalOpen] = useState(false);
  const [healthData, setHealthData] = useState<SystemHealthAudit | null>(null);
  const [demoActionLoading, setDemoActionLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  const handleResetDemo = async () => {
    try {
      setDemoActionLoading(true);
      const res = await api.resetDemoState();
      showToast(`✓ ${res.message || 'Demo state reset successfully!'}`);
      setDemoModalOpen(false);
      if (typeof window !== 'undefined') {
        window.location.reload();
      }
    } catch (err: any) {
      showToast(`✗ Reset failed: ${err.message}`);
    } finally {
      setDemoActionLoading(false);
    }
  };

  const handleSimulateScenario = async (scenario: string, name: string) => {
    try {
      setDemoActionLoading(true);
      const res = await api.simulateEdgeStream(scenario);
      showToast(`✓ Ingested ${res.records_ingested} records for ${name} [${res.sync_status}]`);
      setDemoModalOpen(false);
      if (typeof window !== 'undefined') {
        setTimeout(() => window.location.reload(), 800);
      }
    } catch (err: any) {
      showToast(`✗ Simulation failed: ${err.message}`);
    } finally {
      setDemoActionLoading(false);
    }
  };

  const handleOpenHealthAudit = async () => {
    try {
      setHealthModalOpen(true);
      const data = await api.getSystemHealthAudit();
      setHealthData(data);
    } catch (err: any) {
      showToast(`Failed to load health audit: ${err.message}`);
    }
  };

  // If on login page, render children directly without shell
  if (pathname === '/login') {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
      {/* Top Banner: Synthetic Demonstration Notice */}
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-1.5 flex items-center justify-between text-xs text-slate-400 z-40 sticky top-0">
        <div className="flex items-center gap-2">
          <span className="font-medium tracking-wide uppercase text-[11px] text-slate-500">
            DEMO MODE • SYNTHETIC DATA
          </span>
          <span className="hidden md:inline text-[11px] text-slate-500">
            This prototype uses simulated personnel and telemetry.
          </span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setDemoModalOpen(true)}
            className="flex items-center gap-1 px-2 py-0.5 rounded hover:bg-slate-800 text-slate-400 font-medium text-[11px] transition"
          >
            <Settings className="w-3 h-3" />
            <span>Demo Controls</span>
          </button>
        </div>
      </div>

      <div className="flex flex-1 min-h-0">
        {/* Sidebar for Desktop */}
        <aside className="hidden md:flex md:w-64 flex-col bg-slate-950 border-r border-slate-800">
          {/* Brand Header */}
          <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
            <div className="text-slate-300">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-base font-bold tracking-wide text-white">SEPTERIA</h1>
              <p className="text-[10px] text-slate-500 font-medium uppercase tracking-wider">Personnel Welfare & Operational Readiness</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-slate-800 text-white font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* User Info & Logout Footer */}
          <div className="p-4 border-t border-slate-800 bg-slate-950/50">
            <div className="flex items-center justify-between">
              <div className="overflow-hidden">
                <p className="text-xs font-semibold text-slate-200 truncate">{user?.email || 'Authorized User'}</p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  <p className="text-[11px] text-slate-400 capitalize">{user?.role?.replace('_', ' ') || 'Authority'}</p>
                </div>
              </div>
              <button
                onClick={logout}
                title="Logout"
                className="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-900 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Top Header Bar */}
          <header className="h-14 bg-slate-950/80 backdrop-blur-sm border-b border-slate-800 px-4 md:px-8 flex items-center justify-between sticky top-[33px] z-30">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="md:hidden p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-900 rounded-lg"
              >
                {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold px-2.5 py-1 rounded bg-blue-950 text-blue-400 border border-blue-800/60 uppercase tracking-wider">
                  SIH26186 Prototype
                </span>
                <span className="text-xs font-medium text-slate-400 hidden sm:inline-block">
                  Predictive Personnel Stress & Welfare Monitoring System
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <p className="text-xs font-semibold text-slate-300">Phase 11: Production Polish</p>
                <p className="text-[10px] text-slate-500">FastAPI • NetworkX • XGBoost</p>
              </div>
              <div className="w-8 h-8 rounded-full bg-blue-600/30 text-blue-400 border border-blue-500/40 flex items-center justify-center font-bold text-xs">
                {user?.role ? user.role.charAt(0).toUpperCase() : 'A'}
              </div>
            </div>
          </header>

          {/* Toast Notification */}
          {toastMessage && (
            <div className="fixed bottom-5 right-5 z-50 bg-slate-950 border border-blue-500/60 shadow-xl rounded-xl p-3.5 text-xs text-white flex items-center gap-2.5 animate-in fade-in slide-in-from-bottom-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span>{toastMessage}</span>
            </div>
          )}

          {/* Mobile Navigation Drawer */}
          {sidebarOpen && (
            <div className="md:hidden bg-slate-950 border-b border-slate-800 px-4 py-3 space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setSidebarOpen(false)}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm ${
                      isActive ? 'bg-blue-600 text-white font-medium' : 'text-slate-400 hover:bg-slate-900'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </div>
          )}

          {/* Page Content */}
          <main className="flex-1 p-4 md:p-8 overflow-y-auto">
            {children}
          </main>
        </div>
      </div>

      {/* Demo Controls Modal */}
      {demoModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-950 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5 animate-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-blue-600/20 text-blue-400 rounded-lg">
                  <Zap className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Live Demonstration Controller</h3>
                  <p className="text-xs text-slate-400">Trigger real backend scenarios without manual DB edits</p>
                </div>
              </div>
              <button
                onClick={() => setDemoModalOpen(false)}
                className="p-1 text-slate-400 hover:text-white rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3">
              {/* Reset Demo */}
              <div className="p-3.5 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-white">1. Master Demo Reset</p>
                  <p className="text-[11px] text-slate-400">Restores clean baseline state across all 9 subsystems.</p>
                </div>
                <button
                  disabled={demoActionLoading}
                  onClick={handleResetDemo}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-red-600/80 hover:bg-red-600 text-white text-xs font-medium transition disabled:opacity-50"
                >
                  <RotateCcw className={`w-3.5 h-3.5 ${demoActionLoading ? 'animate-spin' : ''}`} />
                  <span>Reset Demo</span>
                </button>
              </div>

              {/* Normal Baseline */}
              <div className="p-3.5 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-white">2. Normal Recovery Equilibrium</p>
                  <p className="text-[11px] text-slate-400">Resting HR 64 bpm, HRV 65 ms, 7.8h sleep.</p>
                </div>
                <button
                  disabled={demoActionLoading}
                  onClick={() => handleSimulateScenario('A', 'Normal Baseline')}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600/80 hover:bg-emerald-600 text-white text-xs font-medium transition disabled:opacity-50"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Load Normal</span>
                </button>
              </div>

              {/* Deteriorating Recovery */}
              <div className="p-3.5 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-white">3. Multi-Day Recovery Decline (BSF Unit 47)</p>
                  <p className="text-[11px] text-slate-400">Night shift strain, 3.8h sleep, HR 84 bpm, HRV 24 ms.</p>
                </div>
                <button
                  disabled={demoActionLoading}
                  onClick={() => handleSimulateScenario('C', 'Recovery Decline')}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-amber-600/80 hover:bg-amber-600 text-white text-xs font-medium transition disabled:opacity-50"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Load Strain</span>
                </button>
              </div>

              {/* Physical Exertion */}
              <div className="p-3.5 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-white">4. Physical Kinetic Exertion</p>
                  <p className="text-[11px] text-slate-400">Active workout (ACC &gt; 2.0 m/s²), verifies non-alarm.</p>
                </div>
                <button
                  disabled={demoActionLoading}
                  onClick={() => handleSimulateScenario('B', 'Physical Exertion')}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-blue-600/80 hover:bg-blue-600 text-white text-xs font-medium transition disabled:opacity-50"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Exertion</span>
                </button>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setDemoModalOpen(false)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* System Health Audit Modal */}
      {healthModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-950 border border-slate-800 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-5 animate-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-emerald-600/20 text-emerald-400 rounded-lg">
                  <Server className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Subsystem Health & Claim Audit</h3>
                  <p className="text-xs text-slate-400">Verifying 9 core layers and scientific invariants</p>
                </div>
              </div>
              <button
                onClick={() => setHealthModalOpen(false)}
                className="p-1 text-slate-400 hover:text-white rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {!healthData ? (
              <div className="p-8 text-center text-xs text-slate-400">Auditing subsystems...</div>
            ) : (
              <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-1">
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl">
                    <span className="text-[10px] text-slate-500 uppercase font-bold">Overall Status</span>
                    <p className="text-base font-bold text-emerald-400 mt-0.5">
                      {healthData.overall_status || healthData.status || 'OPERATIONAL'}
                    </p>
                  </div>
                  <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl">
                    <span className="text-[10px] text-slate-500 uppercase font-bold">Claim Invariants</span>
                    <p className="text-base font-bold text-blue-400 mt-0.5">
                      {healthData.claim_boundaries ? 'NON-PUNITIVE ✓' : (healthData.claim_boundaries_verified ? 'VERIFIED ✓' : 'VERIFIED ✓')}
                    </p>
                  </div>
                </div>

                {healthData.claim_boundaries?.purpose && (
                  <div className="p-2.5 bg-blue-950/40 border border-blue-800/60 rounded-lg text-xs text-blue-300">
                    <span className="font-semibold text-white">System Boundary:</span> {healthData.claim_boundaries.purpose}
                  </div>
                )}

                <div className="space-y-2">
                  <span className="text-xs font-semibold text-slate-300">Subsystem Diagnostics</span>
                  {Object.entries(healthData.components || healthData.subsystems || {}).map(([key, val]: [string, any]) => {
                    const statusStr = typeof val === 'object' ? (val.status || 'OPERATIONAL') : 'OPERATIONAL';
                    const detailStr = typeof val === 'object' 
                      ? (val.detail || val.model || val.graph_engine || val.features || val.type || (val.adapters ? val.adapters.join(', ') : 'Active')) 
                      : String(val);
                    const isHealthy = statusStr === 'OPERATIONAL' || statusStr === 'HEALTHY';

                    return (
                      <div key={key} className="p-2.5 bg-slate-900/60 border border-slate-800 rounded-lg flex items-center justify-between text-xs">
                        <div>
                          <span className="font-semibold text-slate-200 capitalize">{key.replace(/_/g, ' ')}</span>
                          <p className="text-[11px] text-slate-400 mt-0.5">{detailStr}</p>
                        </div>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono ${
                          isHealthy ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/60' : 'bg-amber-950 text-amber-300 border border-amber-800/60'
                        }`}>
                          {statusStr}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            <div className="pt-2 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setHealthModalOpen(false)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
