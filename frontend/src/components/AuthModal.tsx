import React, { useState } from 'react';
import {
  Lock,
  User,
  ShieldCheck,
  ArrowRight,
  Sparkles,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import { User as UserType } from '../types';

interface Props {
  onLoginSuccess: (user: UserType, token: string) => void;
  onShowToast: (type: 'success' | 'error' | 'info', text: string) => void;
  onCancel?: () => void;
}

export const AuthModal: React.FC<Props> = ({ onLoginSuccess, onShowToast, onCancel }) => {
  const [username, setUsername] = useState('reviewer');
  const [password, setPassword] = useState('reviewer123');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const demoAccounts = [
    { label: 'Reviewer', u: 'reviewer', p: 'reviewer123', desc: 'Authorized to approve content & request changes' },
    { label: 'Creator', u: 'creator', p: 'creator123', desc: 'Drafts content, runs reviews, applies corrections' },
    { label: 'Admin', u: 'admin', p: 'admin123', desc: 'Full administrative access across brands' },
  ];

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.login(username, password);
      localStorage.setItem('brandguard_token', res.access_token);
      localStorage.setItem('brandguard_user', JSON.stringify(res.user));
      onShowToast('success', `Welcome back, ${res.user.full_name} (${res.user.role.toUpperCase()})!`);
      onLoginSuccess(res.user, res.access_token);
    } catch (err: any) {
      setErrorMsg(err.message || 'Login failed. Please verify credentials.');
      onShowToast('error', err.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const selectAccount = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
    setErrorMsg(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-[#111827] border border-[#1f2b42] rounded-2xl max-w-md w-full p-6 space-y-6 shadow-2xl relative overflow-hidden">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-teal-400 flex items-center justify-center shadow-lg shadow-cyan-900/30">
            <Lock className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight">Enterprise Authentication</h2>
            <p className="text-xs text-slate-400">Round 3 Multi-User Governance & RBAC</p>
          </div>
        </div>

        {/* Demo Account Quick Selector */}
        <div className="space-y-2">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
            Hackathon 1-Click Demo Accounts
          </span>
          <div className="grid grid-cols-3 gap-2">
            {demoAccounts.map((acc) => (
              <button
                key={acc.u}
                type="button"
                onClick={() => selectAccount(acc.u, acc.p)}
                className={`p-2 rounded-lg text-left border transition-all text-xs ${
                  username === acc.u
                    ? 'bg-cyan-950/70 border-cyan-500/60 text-cyan-200 shadow-sm'
                    : 'bg-[#141d30] border-[#22314d] text-slate-300 hover:border-slate-600'
                }`}
              >
                <div className="font-bold text-white">{acc.label}</div>
                <div className="text-[10px] text-slate-400 font-mono mt-0.5">{acc.u}</div>
              </button>
            ))}
          </div>
        </div>

        {errorMsg && (
          <div className="p-3 rounded-lg bg-red-950/40 border border-red-500/40 text-red-300 text-xs flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-400 font-medium mb-1">Username</label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-[#162035] border border-[#243350] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500 font-mono text-xs"
            />
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-[#162035] border border-[#243350] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500 font-mono text-xs"
            />
          </div>

          <div className="pt-2 flex items-center justify-between gap-3">
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 rounded-lg text-slate-400 hover:text-white transition-colors"
              >
                Close
              </button>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950 font-bold text-xs hover:from-cyan-400 hover:to-teal-400 transition-all flex items-center justify-center gap-2 shadow-lg shadow-cyan-950/40 disabled:opacity-50"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>{isLoading ? 'Verifying Credentials...' : 'Authenticate Session'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
