import React from 'react';
import { SeverityLevel } from '../types';
import { AlertTriangle, AlertCircle, Info, ShieldAlert } from 'lucide-react';

interface Props {
  severity: SeverityLevel;
  className?: string;
}

export const SeverityBadge: React.FC<Props> = ({ severity, className = '' }) => {
  const config = {
    critical: {
      bg: 'bg-red-950/70 border-red-500/50 text-red-300',
      icon: ShieldAlert,
      label: 'Critical'
    },
    high: {
      bg: 'bg-orange-950/70 border-orange-500/50 text-orange-300',
      icon: AlertTriangle,
      label: 'High'
    },
    medium: {
      bg: 'bg-yellow-950/60 border-yellow-500/50 text-yellow-300',
      icon: AlertCircle,
      label: 'Medium'
    },
    low: {
      bg: 'bg-blue-950/60 border-blue-500/50 text-blue-300',
      icon: Info,
      label: 'Low'
    },
    informational: {
      bg: 'bg-slate-800 border-slate-600 text-slate-300',
      icon: Info,
      label: 'Info'
    }
  }[severity] || {
    bg: 'bg-slate-800 border-slate-600 text-slate-300',
    icon: Info,
    label: severity
  };

  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.bg} ${className}`}>
      <Icon className="w-3.5 h-3.5" />
      <span>{config.label}</span>
    </span>
  );
};
