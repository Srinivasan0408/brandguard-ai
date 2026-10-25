import React, { useState } from 'react';
import {
  History,
  GitCommit,
  CheckCircle2,
  Clock,
  MessageSquare,
  AlertOctagon,
  ArrowRight,
  FileText,
  User,
  ShieldCheck
} from 'lucide-react';
import { ContentItem } from '../types';
import { StatusBadge } from '../components/StatusBadge';

interface Props {
  items: ContentItem[];
  onSelectReview: (item: ContentItem) => void;
}

export const ReviewHistoryPage: React.FC<Props> = ({ items, onSelectReview }) => {
  const [selectedItemId, setSelectedItemId] = useState<string | null>(
    items.length > 0 ? items[0].id : null
  );

  const selectedItem = items.find((i) => i.id === selectedItemId) || (items.length > 0 ? items[0] : null);

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-bold text-white tracking-tight">Governance Review History & Audit Trail</h1>
          <span className="text-xs bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 font-mono px-2 py-0.5 rounded">
            Immutable Revision Log
          </span>
        </div>
        <p className="text-sm text-slate-400 mt-1">
          Traceable historical snapshots, actor accountability, reviewer comments, and version comparisons.
        </p>
      </div>

      {items.length === 0 ? (
        <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-16 text-center space-y-3">
          <History className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">No Audit History Recorded</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Submit and review content in BrandGuard AI to generate traceable revision snapshots and approval event trails.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Item Selector (4 cols) */}
          <div className="lg:col-span-4 bg-[#111827] border border-[#1f2b42] rounded-xl overflow-hidden shadow-sm divide-y divide-[#1f2b42]">
            <div className="p-4 bg-[#141d30] font-semibold text-xs text-slate-300 uppercase tracking-wider flex justify-between items-center">
              <span>Managed Assets</span>
              <span className="text-slate-400">{items.length} records</span>
            </div>

            <div className="divide-y divide-[#1f2b42] max-h-[600px] overflow-y-auto">
              {items.map((item) => {
                const isSelected = item.id === selectedItemId;

                return (
                  <button
                    key={item.id}
                    onClick={() => setSelectedItemId(item.id)}
                    className={`w-full text-left p-4 transition-all hover:bg-[#162035] ${
                      isSelected ? 'bg-[#18233a] border-l-4 border-cyan-400' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span className="font-semibold text-xs text-white truncate max-w-[180px]">
                        {item.title}
                      </span>
                      <StatusBadge status={item.status} />
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-slate-400 mt-1">
                      <span>{item.channel}</span>
                      <span className="font-mono">{item.revisions.length} revisions</span>
                    </div>

                    <div className="text-[10px] text-slate-500 font-mono mt-1">
                      Created {new Date(item.created_at).toLocaleDateString()}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right Column: Revision Snapshots & Audit Trail Timeline (8 cols) */}
          {selectedItem && (
            <div className="lg:col-span-8 space-y-6">
              {/* Revision Comparison Cards */}
              <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-4 shadow-sm">
                <div className="flex items-center justify-between border-b border-[#1f2b42] pb-3">
                  <div className="flex items-center gap-2">
                    <GitCommit className="w-4 h-4 text-cyan-400" />
                    <h3 className="font-semibold text-white text-sm">
                      Revision Snapshots for &ldquo;{selectedItem.title}&rdquo;
                    </h3>
                  </div>
                  <span className="text-xs text-slate-400">
                    Latest: <strong className="text-cyan-300">v{selectedItem.current_revision}</strong>
                  </span>
                </div>

                <div className="space-y-4">
                  {selectedItem.revisions.map((rev) => (
                    <div
                      key={rev.id}
                      className="bg-[#141d30] border border-[#22314d] rounded-lg p-4 space-y-2 text-xs"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded font-mono font-bold bg-cyan-950 text-cyan-300 border border-cyan-500/40 text-[10px]">
                            Revision #{rev.revision_number}
                          </span>
                          <span className="text-slate-300 font-medium">{rev.change_summary || 'Content revision'}</span>
                        </div>
                        <span className="text-slate-500 text-[11px] font-mono">
                          {new Date(rev.created_at).toLocaleString()}
                        </span>
                      </div>

                      <div className="p-3 bg-[#0d1322] border border-[#1a253a] rounded text-slate-200 font-sans leading-relaxed whitespace-pre-wrap">
                        {rev.content_text}
                      </div>

                      <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
                        <User className="w-3 h-3 text-slate-500" />
                        <span>Committed by: {rev.created_by}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Chronological Audit Event Trail */}
              <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-4 shadow-sm">
                <div className="flex items-center gap-2 border-b border-[#1f2b42] pb-3">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <h3 className="font-semibold text-white text-sm">Chronological Governance Event Log</h3>
                </div>

                {selectedItem.approval_history.length === 0 ? (
                  <div className="text-xs text-slate-500 py-4 text-center">No audit events logged yet.</div>
                ) : (
                  <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#22314d]">
                    {selectedItem.approval_history.map((evt, idx) => (
                      <div key={evt.id || idx} className="relative space-y-1 text-xs">
                        {/* Dot indicator */}
                        <div
                          className={`absolute -left-6 top-1 w-2.5 h-2.5 rounded-full ring-4 ring-[#111827] ${
                            evt.event_type === 'approved'
                              ? 'bg-emerald-400'
                              : evt.event_type === 'changes_requested'
                              ? 'bg-amber-400'
                              : evt.event_type === 'in_review' || evt.event_type === 'submitted'
                              ? 'bg-cyan-400'
                              : 'bg-slate-400'
                          }`}
                        />

                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-white uppercase text-[11px] tracking-wide">
                            {evt.event_type.replace('_', ' ')}
                          </span>
                          <span className="text-[11px] font-mono text-slate-500">
                            {new Date(evt.created_at).toLocaleString()}
                          </span>
                        </div>

                        <p className="text-slate-300">{evt.comments || 'Status updated.'}</p>

                        <div className="text-[11px] text-slate-400 flex items-center gap-2">
                          <span>
                            Actor: <strong className="text-slate-200">{evt.actor_name}</strong>
                          </span>
                          <span>&bull;</span>
                          <span className="capitalize font-mono text-slate-400">Role: {evt.actor_role}</span>
                          <span>&bull;</span>
                          <span className="font-mono text-slate-500">Revision #{evt.revision_number}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Reviewer Comments Log */}
              {selectedItem.comments.length > 0 && (
                <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-3">
                  <div className="flex items-center gap-2 border-b border-[#1f2b42] pb-3">
                    <MessageSquare className="w-4 h-4 text-violet-400" />
                    <h3 className="font-semibold text-white text-sm">Reviewer Comments & Feedback Notes</h3>
                  </div>

                  <div className="space-y-3">
                    {selectedItem.comments.map((cmt) => (
                      <div
                        key={cmt.id}
                        className="bg-[#141d30] border border-[#22314d] rounded-lg p-3 space-y-1 text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-slate-200">{cmt.author_name} ({cmt.author_role})</span>
                          <span className="text-[11px] text-slate-500 font-mono">
                            {new Date(cmt.created_at).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-slate-300 leading-relaxed">&ldquo;{cmt.comment_text}&rdquo;</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
