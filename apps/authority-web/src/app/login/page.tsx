'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { Shield, Lock, Mail, AlertCircle, KeyRound, Sparkles } from 'lucide-react';

// Development-only test accounts (for form quick-fill ONLY; strictly triggers real JWT backend login)
const DEV_ACCOUNTS = [
  {
    role: 'Admin',
    email: 'admin@septeria.gov.in',
    password: 'SepteriaAdmin2026!',
    badge: 'MHA HQ',
  },
  {
    role: 'Commander',
    email: 'commander.bsf47@septeria.gov.in',
    password: 'Commander2026!',
    badge: 'BSF Unit 47',
  },
  {
    role: 'Welfare Officer',
    email: 'welfare.crpf@septeria.gov.in',
    password: 'Welfare2026!',
    badge: 'CRPF Unit 102',
  },
  {
    role: 'Medical Officer',
    email: 'medical.itbp@septeria.gov.in',
    password: 'Medical2026!',
    badge: 'ITBP Unit 18',
  },
];

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();

  const isDevMode = process.env.NODE_ENV !== 'production' || process.env.NEXT_PUBLIC_ENABLE_DEV_AUTH_QUICKFILL === 'true';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickFill = (acc: typeof DEV_ACCOUNTS[0]) => {
    setEmail(acc.email);
    setPassword(acc.password);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* System Header */}
        <div className="flex justify-center">
          <div className="w-12 h-12 rounded border border-slate-700 flex items-center justify-center text-slate-300 bg-slate-900 shadow-sm">
            <Shield className="w-6 h-6" />
          </div>
        </div>
        <h2 className="mt-4 text-center text-2xl font-bold tracking-tight text-white">
          SEPTERIA
        </h2>
        <p className="mt-1 text-center text-xs font-medium text-slate-400 uppercase tracking-wider">
          Personnel Welfare & Support Portal
        </p>
        <p className="mt-1 text-center text-xs text-slate-500">
          SIH26186 Prototype • Phase 1
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-slate-900 py-8 px-4 border border-slate-800 sm:rounded-lg sm:px-10">
          {error && (
            <div className="mb-6 p-3 rounded-lg bg-red-950/60 border border-red-800/80 flex items-start gap-2.5 text-red-300 text-xs">
              <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="block text-xs font-medium text-slate-300">
                Official ID / Email
              </label>
              <div className="mt-1.5 relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="ID / Email"
                  className="block w-full pl-10 pr-3.5 py-2.5 bg-slate-800/50 border border-slate-700 rounded text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-slate-500 transition-all"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-xs font-medium text-slate-300">
                Password
              </label>
              <div className="mt-1.5 relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="block w-full pl-10 pr-3.5 py-2.5 bg-slate-800/50 border border-slate-700 rounded text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-slate-500 transition-all"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex justify-center items-center gap-2 py-2.5 px-4 border border-transparent rounded text-sm font-medium text-white bg-slate-800 hover:bg-slate-700 focus:outline-none transition-all"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin"></div>
                    <span>Authenticating...</span>
                  </>
                ) : (
                  <span>Secure Sign In</span>
                )}
              </button>
            </div>
          </form>

          {/* Development-Only Credential Quick-Fill Section */}
          {isDevMode && (
            <div className="mt-8 pt-6 border-t border-slate-800">
              <div className="flex items-center gap-2 mb-3">
                <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                  Demonstration Quick-Fill (Synthetic Data)
                </p>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {DEV_ACCOUNTS.map((acc) => (
                  <button
                    key={acc.email}
                    type="button"
                    onClick={() => handleQuickFill(acc)}
                    className="p-2 rounded-lg bg-slate-950/70 border border-slate-800/80 hover:border-blue-500/50 text-left transition-all group"
                  >
                    <p className="text-xs font-semibold text-slate-200 group-hover:text-blue-400 transition-colors">
                      {acc.role}
                    </p>
                    <p className="text-[10px] text-slate-500 truncate">{acc.badge}</p>
                  </button>
                ))}
              </div>
              <p className="text-[10px] text-slate-500 mt-2 italic text-center">
                * Populates test credentials for authenticating against the FastAPI backend.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
