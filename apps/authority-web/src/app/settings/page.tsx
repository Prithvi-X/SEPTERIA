'use client';

import React from 'react';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { Settings, ShieldCheck, Database, Key } from 'lucide-react';

export default function SettingsPage() {
  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <div className="space-y-6 max-w-4xl">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight uppercase">System Administration</h1>
            <p className="text-xs font-medium text-slate-400 mt-1 uppercase tracking-wider">
              Security Policies & Backend Status
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-5 bg-slate-950 border border-slate-800 rounded space-y-3">
            <div className="flex items-center gap-2 text-slate-300 text-xs font-bold uppercase tracking-wider border-b border-slate-800 pb-2">
              <Database className="w-4 h-4 text-slate-500" />
              <span>Database Connection</span>
            </div>
            <p className="text-sm font-medium text-slate-200 mt-2">
              <span className="text-emerald-500 font-bold mr-2">●</span>
              PostgreSQL 16 (Operational)
            </p>
            <p className="text-xs text-slate-500 leading-relaxed">
              Serving production schema. Connected securely.
            </p>
          </div>

          <div className="p-5 bg-slate-950 border border-slate-800 rounded space-y-3">
            <div className="flex items-center gap-2 text-slate-300 text-xs font-bold uppercase tracking-wider border-b border-slate-800 pb-2">
              <Key className="w-4 h-4 text-slate-500" />
              <span>Authentication Standard</span>
            </div>
            <p className="text-sm font-medium text-slate-200 mt-2">
              <span className="text-blue-500 font-bold mr-2">●</span>
              JWT (HS256) / Bcrypt
            </p>
            <p className="text-xs text-slate-500 leading-relaxed">
              RBAC enforcement active for Commander, Welfare, Medical, and Admin roles.
            </p>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded p-8 flex flex-col items-center justify-center text-center mt-6">
          <Settings className="w-8 h-8 text-slate-600 mb-3" />
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest">Audit Trails (Pending)</h3>
          <p className="text-xs text-slate-500 mt-2 max-w-sm">
            Comprehensive audit log viewing is scheduled for Phase 12 deployment. Current logs are retained securely in the backend.
          </p>
        </div>
      </div>
    </ProtectedRoute>
  );
}
