'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
}

export function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { user, isLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center gap-3">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm text-slate-400 font-medium">Verifying authorization...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return (
      <div className="bg-red-950/40 border border-red-800/60 rounded-xl p-6 text-center max-w-lg mx-auto mt-12">
        <h2 className="text-lg font-semibold text-red-300">Access Restricted</h2>
        <p className="text-sm text-slate-400 mt-2">
          Your current role (<span className="text-slate-200 font-mono">{user.role}</span>) does not have permission to view this section.
        </p>
      </div>
    );
  }

  return <>{children}</>;
}
