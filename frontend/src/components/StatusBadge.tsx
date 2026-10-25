import React from 'react';
import { ContentStatus } from '../types';
import { CheckCircle2, Clock, AlertOctagon, XCircle, FileEdit } from 'lucide-react';

interface Props {
  status: ContentStatus;
  className?: string;
}

export const StatusBadge: React.FC<Props> = ({ status, className = '' }) => {
  const config = {
    draft: {
      bg: 'bg-slate-800 border-slate-700 text-slate-300',
      icon: FileEdit,
      label: 'Draft'
    },
    in_review: {
      bg: 'bg-cyan-950/80 border-cyan-500/50 text-cyan-300',
      icon: Clock,
      label: 'In Review'
    },
    changes_requested: {
      bg: 'bg-amber-950/80 border-amber-500/50 text-amber-300',
      icon: AlertOctagon,
      label: 'Changes Requested'
    },
    approved: {
      bg: 'bg-emerald-950/80 border-emerald-500/50 text-emerald-300',
      icon: CheckCircle2,
      label: 'Approved'
    },
    rejected: {
      bg: 'bg-rose-950/80 border-rose-500/50 text-rose-300',
      icon: XCircle,
      label: 'Rejected'
    }
  }[status] || {
    bg: 'bg-slate-800 border-slate-700 text-slate-300',
    icon: FileEdit,
    label: status
  };

  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${config.bg} ${className}`}>
      <Icon className="w-3.5 h-3.5" />
      <span>{config.label}</span>
    </span>
  );
};
