'use client';

import { Shield, Smartphone, ArrowRight, ExternalLink } from 'lucide-react';
import Link from 'next/link';

export default function GatewayPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 flex flex-col items-center justify-center p-6 font-sans">
      <div className="max-w-3xl w-full">
        {/* Header Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-blue-500/10 text-blue-400 mb-6 border border-blue-500/20 shadow-[0_0_30px_-5px_rgba(59,130,246,0.3)]">
            <Shield className="w-10 h-10" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight">SEPTERIA Prototype</h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            SIH26186 • AI-Based Predictive Personnel Stress & Welfare Monitoring System
          </p>
        </div>

        {/* Judges Note */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 mb-8 relative overflow-hidden shadow-lg">
          <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
          <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
            Important Note for Evaluators
          </h3>
          <p className="text-slate-400 text-sm leading-relaxed">
            SEPTERIA is a dual-platform ecosystem. To fully evaluate the prototype, please explore both the <strong className="text-slate-300">Personnel Mobile App</strong> (designed for frontline personnel) and the <strong className="text-slate-300">Authority Command Portal</strong> (designed for commanders and medical staff).
          </p>
        </div>

        {/* The Two Platforms */}
        <div className="grid md:grid-cols-2 gap-6">
          
          {/* Mobile App Card */}
          <a 
            href="https://prithvi-x.github.io" 
            target="_blank" 
            rel="noopener noreferrer"
            className="group block p-8 rounded-2xl bg-slate-900 border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-800/80 hover:shadow-[0_0_30px_-10px_rgba(99,102,241,0.3)] transition-all duration-300"
          >
            <div className="w-12 h-12 rounded-full bg-indigo-500/10 text-indigo-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Smartphone className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold text-white mb-3 flex items-center justify-between">
              Personnel App
              <ExternalLink className="w-5 h-5 text-slate-500 group-hover:text-indigo-400 transition-colors" />
            </h2>
            <p className="text-slate-400 text-sm mb-6 min-h-[60px]">
              The Flutter-based mobile PWA for frontline personnel. Features privacy-first AI stress tracking and decentralized data ingestion.
            </p>
            <div className="flex items-center text-sm font-medium text-indigo-400">
              Launch Mobile App <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
            </div>
          </a>

          {/* Authority Portal Card */}
          <Link 
            href="/login"
            className="group block p-8 rounded-2xl bg-slate-900 border border-slate-800 hover:border-emerald-500/50 hover:bg-slate-800/80 hover:shadow-[0_0_30px_-10px_rgba(16,185,129,0.3)] transition-all duration-300"
          >
            <div className="w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Shield className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold text-white mb-3 flex items-center justify-between">
              Authority Portal
              <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-emerald-400 transition-colors" />
            </h2>
            <p className="text-slate-400 text-sm mb-6 min-h-[60px]">
              The Next.js operational dashboard for commanders. Features the Contextual Graph Engine and Tri-Layer ML pipeline.
            </p>
            <div className="flex items-center text-sm font-medium text-emerald-400">
              Enter Dashboard <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

        </div>

      </div>
    </div>
  );
}
