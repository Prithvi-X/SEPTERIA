'use client';

import { useEffect } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('App runtime error:', error);
  }, [error]);

  return (
    <div className="min-h-[50vh] flex flex-col items-center justify-center gap-4 text-center px-4">
      <div className="p-3 bg-red-950/60 border border-red-800/80 rounded-xl text-red-400">
        <AlertCircle className="w-8 h-8" />
      </div>
      <div>
        <h2 className="text-base font-semibold text-white">An unexpected error occurred</h2>
        <p className="text-xs text-slate-400 mt-1 max-w-sm">
          {error.message || 'Something went wrong while rendering this section.'}
        </p>
      </div>
      <button
        onClick={() => reset()}
        className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition-all"
      >
        <RefreshCw className="w-3.5 h-3.5" />
        <span>Try Again</span>
      </button>
    </div>
  );
}
