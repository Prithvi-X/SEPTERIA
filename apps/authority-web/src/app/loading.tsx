'use client';

export default function Loading() {
  return (
    <div className="min-h-[50vh] flex flex-col items-center justify-center gap-3">
      <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      <p className="text-xs text-slate-400 font-medium">Loading content...</p>
    </div>
  );
}
