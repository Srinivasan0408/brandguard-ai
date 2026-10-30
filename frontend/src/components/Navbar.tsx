import React from 'react';
import { ShieldCheck, UserCheck, RefreshCw, Cpu, Database, LogIn, LogOut, User } from 'lucide-react';
import { HealthStatus, User as UserType } from '../types';

interface Props {
  currentRole: 'creator' | 'reviewer';
  onRoleChange: (role: 'creator' | 'reviewer') => void;
  currentUser: UserType | null;
  onOpenAuth: () => void;
  onLogout: () => void;
  health: HealthStatus | null;
  onResetDemo: () => void;
  isResetting: boolean;
}

export const Navbar: React.FC<Props> = ({
  currentRole,
  onRoleChange,
  currentUser,
  onOpenAuth,
  onLogout,
  health,
  onResetDemo,
  isResetting
}) => {
  const isLLM = health?.review_engine?.llm_configured;
  const isSupabase = health?.database?.type === 'supabase';

  return (
    <header className="h-16 bg-[#0d1322] border-b border-[#1f2b42] flex items-center justify-between px-6 sticky top-0 z-40 shadow-sm">
      {/* Brand & Tagline */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-teal-400 flex items-center justify-center shadow-lg shadow-cyan-900/30">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-white tracking-tight">BrandGuard<span className="text-cyan-400">.AI</span></span>
              <span className="text-[10px] bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 font-mono px-1.5 py-0.5 rounded uppercase">
                Round 3 Final
              </span>
            </div>
            <p className="text-xs text-slate-400 font-normal hidden sm:block">Create Freely. Publish Confidently.</p>
          </div>
        </div>
      </div>

      {/* System Status Indicators & Authenticated User or Role Selector */}
      <div className="flex items-center gap-3">
        {/* Analysis Engine Mode */}
        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#162035] border border-[#243350] text-xs">
          <Cpu className={`w-3.5 h-3.5 ${isLLM ? 'text-teal-400 animate-pulse' : 'text-cyan-400'}`} />
          <span className="text-slate-400">Engine:</span>
          <span className="text-slate-200 font-medium">
            {isLLM ? 'AI-Assisted Hybrid' : 'Deterministic Grounded'}
          </span>
        </div>

        {/* Database Mode */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#162035] border border-[#243350] text-xs">
          <Database className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-400">Storage:</span>
          <span className="text-slate-200 font-medium">
            {isSupabase ? 'Supabase PostgreSQL' : 'Local SQLite Persistence'}
          </span>
        </div>

        {/* User Account / Role Pill */}
        {currentUser ? (
          <div className="flex items-center gap-2 bg-[#141d30] border border-[#243350] rounded-lg px-2.5 py-1 text-xs">
            <div className="flex items-center gap-1.5 text-slate-300">
              <User className="w-3.5 h-3.5 text-cyan-400" />
              <span className="font-medium text-white">{currentUser.username}</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#1c2942] border border-[#2c3d60] font-mono font-bold uppercase text-cyan-300">
                {currentUser.role}
              </span>
            </div>
            <button
              onClick={onLogout}
              className="text-slate-400 hover:text-rose-400 p-0.5 rounded transition-colors ml-1"
              title="Logout session"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            {/* Simulated Role Switcher for Instant Demo Testing */}
            <div className="flex items-center bg-[#131b2e] border border-[#243350] rounded-lg p-0.5 text-xs">
              <button
                onClick={() => onRoleChange('creator')}
                className={`px-2.5 py-1 rounded-md transition-all font-medium flex items-center gap-1 ${
                  currentRole === 'creator'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Simulate Creator (Drafts, Edits)"
              >
                <span>Creator</span>
              </button>
              <button
                onClick={() => onRoleChange('reviewer')}
                className={`px-2.5 py-1 rounded-md transition-all font-medium flex items-center gap-1 ${
                  currentRole === 'reviewer'
                    ? 'bg-violet-500/20 text-violet-300 border border-violet-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Simulate Reviewer (Approvals, Change Requests)"
              >
                <UserCheck className="w-3 h-3 text-violet-400" />
                <span>Reviewer</span>
              </button>
            </div>

            <button
              onClick={onOpenAuth}
              className="px-3 py-1 rounded-lg bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950 font-bold text-xs hover:from-cyan-400 hover:to-teal-400 transition-all flex items-center gap-1.5 shadow-sm"
              title="Login with secure credentials"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Login</span>
            </button>
          </div>
        )}

        {/* Reset Demo Button */}
        <button
          onClick={onResetDemo}
          disabled={isResetting}
          className="p-1.5 text-slate-400 hover:text-cyan-400 hover:bg-[#162035] rounded-lg transition-colors border border-transparent hover:border-[#243350]"
          title="Reset demonstration data"
        >
          <RefreshCw className={`w-4 h-4 ${isResetting ? 'animate-spin text-cyan-400' : ''}`} />
        </button>
      </div>
    </header>
  );
};
