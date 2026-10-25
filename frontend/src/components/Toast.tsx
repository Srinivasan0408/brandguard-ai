import React, { useEffect } from 'react';
import { CheckCircle2, AlertTriangle, X } from 'lucide-react';

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info';
  text: string;
}

interface Props {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const ToastContainer: React.FC<Props> = ({ toasts, onDismiss }) => {
  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-md w-full pointer-events-none">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={() => onDismiss(toast.id)} />
      ))}
    </div>
  );
};

const ToastItem: React.FC<{ toast: ToastMessage; onDismiss: () => void }> = ({ toast, onDismiss }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onDismiss();
    }, 4500);
    return () => clearTimeout(timer);
  }, [onDismiss]);

  const isSuccess = toast.type === 'success';
  const isError = toast.type === 'error';

  return (
    <div
      className={`pointer-events-auto flex items-start justify-between gap-3 p-4 rounded-lg shadow-xl border text-sm transition-all animate-in slide-in-from-bottom-5 ${
        isSuccess
          ? 'bg-emerald-950/90 border-emerald-500/60 text-emerald-100'
          : isError
          ? 'bg-rose-950/90 border-rose-500/60 text-rose-100'
          : 'bg-slate-900 border-slate-700 text-slate-100'
      }`}
    >
      <div className="flex items-start gap-2.5">
        {isSuccess ? (
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        ) : (
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
        )}
        <span className="leading-snug">{toast.text}</span>
      </div>
      <button
        onClick={onDismiss}
        className="text-slate-400 hover:text-white transition-colors p-0.5 rounded"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};
