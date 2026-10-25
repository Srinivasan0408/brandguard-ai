import React, { useState } from 'react';
import {
  Settings,
  ShieldCheck,
  Cpu,
  Database,
  Lock,
  RefreshCw,
  AlertTriangle,
  Info,
  CheckCircle2,
  ExternalLink
} from 'lucide-react';
import { HealthStatus } from '../types';

interface Props {
  health: HealthStatus | null;
  onResetDemo: () => void;
  isResetting: boolean;
  onShowToast: (type: 'success' | 'error' | 'info', text: string) => void;
}

export const SettingsPage: React.FC<Props> = ({
  health,
  onResetDemo,
  isResetting,
  onShowToast
}) => {
  const isLLMConfigured = health?.review_engine?.llm_configured;
  const isSupabase = health?.database?.type === 'supabase';

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-bold text-white tracking-tight">System Settings & Governance Policies</h1>
          <span className="text-xs bg-slate-800 border border-slate-700 text-slate-300 font-mono px-2 py-0.5 rounded">
            v{health?.version || '2.0.0'}
          </span>
        </div>
        <p className="text-sm text-slate-400 mt-1">
          Diagnostics, infrastructure connectivity, responsible AI disclosures, and data isolation controls.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Review Engine & AI Configuration */}
        <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-4 shadow-sm">
          <div className="flex items-center gap-2 border-b border-[#1f2b42] pb-3">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <h2 className="font-semibold text-white text-sm">Review Engine & Analysis Mode</h2>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-lg bg-[#141d30] border border-[#22314d]">
              <div>
                <span className="text-slate-400 block">Active Engine Mode:</span>
                <span className="font-bold text-white text-sm">
                  {isLLMConfigured ? 'AI-Assisted Hybrid Analysis' : 'Deterministic Rule Engine'}
                </span>
              </div>
              <span
                className={`px-2.5 py-1 rounded-full text-[11px] font-semibold border ${
                  isLLMConfigured
                    ? 'bg-teal-950 border-teal-500/40 text-teal-300'
                    : 'bg-cyan-950 border-cyan-500/40 text-cyan-300'
                }`}
              >
                {isLLMConfigured ? 'LLM Active' : 'Deterministic Active'}
              </span>
            </div>

            <div className="p-3.5 rounded-lg bg-[#162035] border border-[#243350] space-y-2 text-slate-300 leading-relaxed">
              <strong className="text-white block">Deterministic Engine Fallback:</strong>
              When no external LLM API key (<code className="text-cyan-300">OPENAI_API_KEY</code> or{' '}
              <code className="text-cyan-300">GEMINI_API_KEY</code>) is supplied in the environment, BrandGuard AI
              operates 100% deterministically using regex boundaries, structured product facts, and exact guideline matchers.
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-[#141d30] border border-[#22314d]">
              <span className="text-slate-400">External LLM Provider:</span>
              <span className="font-mono text-slate-200">
                {health?.review_engine?.llm_provider || 'None (Deterministic fallback)'}
              </span>
            </div>
          </div>
        </div>

        {/* Right: Storage & Supabase Diagnostics */}
        <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-4 shadow-sm">
          <div className="flex items-center gap-2 border-b border-[#1f2b42] pb-3">
            <Database className="w-4 h-4 text-teal-400" />
            <h2 className="font-semibold text-white text-sm">Database & Persistence Layer</h2>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-lg bg-[#141d30] border border-[#22314d]">
              <div>
                <span className="text-slate-400 block">Connected Storage Engine:</span>
                <span className="font-bold text-white text-sm">
                  {isSupabase ? 'Supabase Managed PostgreSQL' : 'Local SQLite Persistence'}
                </span>
              </div>
              <span
                className={`px-2.5 py-1 rounded-full text-[11px] font-semibold border ${
                  isSupabase
                    ? 'bg-emerald-950 border-emerald-500/40 text-emerald-300'
                    : 'bg-cyan-950 border-cyan-500/40 text-cyan-300'
                }`}
              >
                {isSupabase ? 'Cloud PostgreSQL' : 'SQLite Local'}
              </span>
            </div>

            <div className="p-3.5 rounded-lg bg-[#162035] border border-[#243350] space-y-2 text-slate-300 leading-relaxed">
              <strong className="text-white block">Zero-Setup Demo Capability:</strong>
              To allow hackathon judges to test without provisioning Supabase keys, BrandGuard AI seamlessly runs on a
              self-contained local SQLite schema with pre-seeded NovaTech data and full relational integrity.
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-[#141d30] border border-[#22314d]">
              <span className="text-slate-400">Active Brands in Storage:</span>
              <span className="font-mono text-cyan-300 font-bold">
                {health?.database?.brands_loaded ?? 1} brand(s)
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Responsible AI & Data Security Governance Policies */}
      <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-4">
        <div className="flex items-center gap-2 border-b border-[#1f2b42] pb-3">
          <Lock className="w-4 h-4 text-emerald-400" />
          <h2 className="font-semibold text-white text-sm">Responsible AI & Data Privacy Safeguards</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-300 leading-relaxed">
          <div className="p-3.5 rounded-lg bg-[#141d30] border border-[#22314d] space-y-1.5">
            <h3 className="font-bold text-white flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Zero Automatic Publishing</span>
            </h3>
            <p className="text-slate-400">
              BrandGuard AI will never publish content automatically. All pre-publication state transitions require explicit
              human reviewer validation.
            </p>
          </div>

          <div className="p-3.5 rounded-lg bg-[#141d30] border border-[#22314d] space-y-1.5">
            <h3 className="font-bold text-white flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-cyan-400" />
              <span>Secrets & Key Isolation</span>
            </h3>
            <p className="text-slate-400">
              API keys and database credentials are read strictly from backend environment variables and are never exposed
              to the client browser.
            </p>
          </div>

          <div className="p-3.5 rounded-lg bg-[#141d30] border border-[#22314d] space-y-1.5">
            <h3 className="font-bold text-white flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-violet-400" />
              <span>External AI Transmission Disclosure</span>
            </h3>
            <p className="text-slate-400">
              When an LLM provider is configured, only the submitted copy snippet is evaluated for tone analysis. Brand
              secrets remain isolated.
            </p>
          </div>
        </div>
      </div>

      {/* Demo Reset Card */}
      <div className="bg-[#111827] border border-red-500/30 rounded-xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-bold text-white">Reset Demo Database to Initial State</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Clears all temporary test reviews and re-seeds the standard NovaTech brand guidelines and approved facts.
          </p>
        </div>

        <button
          onClick={onResetDemo}
          disabled={isResetting}
          className="px-4 py-2 rounded-lg bg-red-950/80 hover:bg-red-900 border border-red-500/50 text-red-200 font-bold text-xs flex items-center gap-2 transition-colors disabled:opacity-50 shrink-0"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isResetting ? 'animate-spin' : ''}`} />
          <span>{isResetting ? 'Resetting Data...' : 'Reset Demonstration Data'}</span>
        </button>
      </div>
    </div>
  );
};
