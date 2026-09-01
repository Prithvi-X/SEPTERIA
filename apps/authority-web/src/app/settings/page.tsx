'use client';

import React from 'react';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { Settings, ShieldCheck, Database, Key } from 'lucide-react';

export default function SettingsPage() {
  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-5">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">System & Security Settings</h1>
            <p className="text-xs text-slate-400 mt-1">
              Role permissions, audit logging policies, and database connection status
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-5 bg-slate-950/70 border border-slate-800 rounded-xl space-y-3">
            <div className="flex items-center gap-2 text-blue-400 text-sm font-semibold">
              <Database className="w-4 h-4" />
              <span>Database Target</span>
            </div>
            <p className="text-xs text-slate-300">
              Target: <span className="font-mono text-emerald-400">PostgreSQL 16</span>
            </p>
            <p className="text-[11px] text-slate-500">
              Single relational database target across development, testing, and deployment.
            </p>
          </div>

          <div className="p-5 bg-slate-950/70 border border-slate-800 rounded-xl space-y-3">
            <div className="flex items-center gap-2 text-purple-400 text-sm font-semibold">
              <Key className="w-4 h-4" />
              <span>Authentication Standard</span>
            </div>
            <p className="text-xs text-slate-300">
              JWT with HS256 / SHA-256 + Bcrypt password hashing
            </p>
            <p className="text-[11px] text-slate-500">
              Backend RBAC enforcement across 5 distinct force roles.
            </p>
          </div>
        </div>

        <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-8 text-center">
          <Settings className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-sm font-semibold text-slate-300">System Administration</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
            Audit trail viewer and user management controls will be implemented in subsequent phases.
          </p>
        </div>
      </div>
    </ProtectedRoute>
  );
}
