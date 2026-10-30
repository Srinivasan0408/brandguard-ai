import React, { useState } from 'react';
import {
  Inbox,
  CheckCircle2,
  XCircle,
  AlertOctagon,
  Clock,
  UserCheck,
  ShieldAlert,
  MessageSquare,
  FileText,
  AlertTriangle,
  Send
} from 'lucide-react';
import { ContentItem } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { SeverityBadge } from '../components/SeverityBadge';
import { api } from '../services/api';

interface Props {
  queueItems: ContentItem[];
  userRole: 'creator' | 'reviewer';
  onItemUpdated: () => void;
  onShowToast: (type: 'success' | 'error' | 'info', text: string) => void;
  onSelectRole: (role: 'creator' | 'reviewer') => void;
}

export const ReviewQueuePage: React.FC<Props> = ({
  queueItems,
  userRole,
  onItemUpdated,
  onShowToast,
  onSelectRole
}) => {
  const [selectedItemId, setSelectedItemId] = useState<string | null>(
    queueItems.length > 0 ? queueItems[0].id : null
  );

  const [reviewerComment, setReviewerComment] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  // Active selected item
  const selectedItem =
    queueItems.find((i) => i.id === selectedItemId) ||
    (queueItems.length > 0 ? queueItems[0] : null);

  // Reject Handler
  const handleReject = async () => {
    if (!selectedItem) return;
    if (!reviewerComment.trim()) {
      onShowToast('error', 'Please provide feedback in the comment box explaining why content is rejected.');
      return;
    }

    setIsProcessing(true);
    try {
      await api.rejectReview(selectedItem.id, {
        actor_name: `Reviewer (${userRole})`,
        actor_role: userRole,
        comments: reviewerComment
      });
      onShowToast('info', `Content "${selectedItem.title}" has been rejected.`);
      setReviewerComment('');
      onItemUpdated();
    } catch (err: any) {
      onShowToast('error', err.message || 'Reject action failed');
    } finally {
      setIsProcessing(false);
    }
  };

  // Approve Handler
  const handleApprove = async () => {
    if (!selectedItem) return;
    setIsProcessing(true);

    try {
      await api.approveReview(selectedItem.id, {
        actor_name: `Reviewer (${userRole})`,
        actor_role: userRole,
        comments: reviewerComment || 'Approved for public release across official channels.'
      });
      onShowToast('success', `Content "${selectedItem.title}" marked as Approved!`);
      setReviewerComment('');
      onItemUpdated();
    } catch (err: any) {
      onShowToast('error', err.message || 'Approval rejected');
    } finally {
      setIsProcessing(false);
    }
  };

  // Request Changes Handler
  const handleRequestChanges = async () => {
    if (!selectedItem) return;
    if (!reviewerComment.trim()) {
      onShowToast('error', 'Please provide feedback in the comment box explaining required changes.');
      return;
    }

    setIsProcessing(true);
    try {
      await api.requestChanges(selectedItem.id, {
        actor_name: `Reviewer (${userRole})`,
        actor_role: userRole,
        comments: reviewerComment
      });
      onShowToast('info', `Returned "${selectedItem.title}" with change requests.`);
      setReviewerComment('');
      onItemUpdated();
    } catch (err: any) {
      onShowToast('error', err.message || 'Action failed');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Governance Review Queue</h1>
            <span className="text-xs bg-amber-950/80 border border-amber-500/40 text-amber-300 font-mono px-2 py-0.5 rounded">
              {queueItems.length} Awaiting Inspection
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Authorised human-in-the-loop review cockpit for pre-publication gatekeeping and editorial sign-offs.
          </p>
        </div>

        {/* Role Notice */}
        <div className="flex items-center gap-2 bg-[#141d30] border border-[#22314d] px-3 py-1.5 rounded-lg text-xs">
          <span className="text-slate-400">Current Role:</span>
          <span className={`font-semibold capitalize ${userRole === 'reviewer' ? 'text-violet-300' : 'text-cyan-300'}`}>
            {userRole}
          </span>
          {userRole !== 'reviewer' && (
            <button
              onClick={() => onSelectRole('reviewer')}
              className="ml-2 text-[11px] underline text-violet-400 hover:text-violet-300 font-medium"
            >
              Switch to Reviewer &rarr;
            </button>
          )}
        </div>
      </div>

      {userRole !== 'reviewer' && (
        <div className="bg-amber-950/40 border border-amber-500/40 rounded-xl p-4 flex items-start gap-3 text-xs leading-relaxed text-amber-200">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <strong>RBAC Enforcement Notice:</strong> You are currently simulating the <em>Creator</em> role.
            Under enterprise governance policy, approval and change-request decisions require an authorized
            <em>Reviewer</em> role. Switch roles above or in the navigation bar to execute sign-offs.
          </div>
        </div>
      )}

      {queueItems.length === 0 ? (
        <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-16 text-center space-y-3">
          <Inbox className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">Review Queue is Empty</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            All submitted content has been processed. Creators can submit drafts from the Content Review tab.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: List of items (4 columns) */}
          <div className="lg:col-span-4 bg-[#111827] border border-[#1f2b42] rounded-xl overflow-hidden shadow-sm divide-y divide-[#1f2b42]">
            <div className="p-4 bg-[#141d30] font-semibold text-xs text-slate-300 uppercase tracking-wider">
              Pending Submissions ({queueItems.length})
            </div>

            <div className="divide-y divide-[#1f2b42] max-h-[600px] overflow-y-auto">
              {queueItems.map((item) => {
                const isSelected = item.id === selectedItemId;
                const critCount = item.latest_review?.critical_count || 0;

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

                    <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2">
                      <span>{item.channel}</span>
                      <span className="font-mono">Rev #{item.current_revision}</span>
                    </div>

                    {critCount > 0 && (
                      <div className="mt-2 text-[10px] text-red-400 font-semibold flex items-center gap-1">
                        <ShieldAlert className="w-3 h-3" />
                        <span>{critCount} critical violations flagged</span>
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right Column: Detailed Inspector (8 columns) */}
          {selectedItem && (
            <div className="lg:col-span-8 bg-[#111827] border border-[#1f2b42] rounded-xl p-6 space-y-6 shadow-sm">
              {/* Item Header */}
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#1f2b42] pb-4">
                <div>
                  <h2 className="text-lg font-bold text-white">{selectedItem.title}</h2>
                  <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                    <span>Channel: <strong className="text-slate-200">{selectedItem.channel}</strong></span>
                    <span>&bull;</span>
                    <span>Submitted by: <strong className="text-slate-200">{selectedItem.created_by}</strong></span>
                    <span>&bull;</span>
                    <span className="font-mono">Rev #{selectedItem.current_revision}</span>
                  </div>
                </div>

                <StatusBadge status={selectedItem.status} />
              </div>

              {/* Submitted Content Display */}
              <div className="space-y-2">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                  Submitted Copy Text
                </span>
                <div className="p-4 rounded-lg bg-[#0d1322] border border-[#1f2b42] text-sm text-slate-200 leading-relaxed font-sans whitespace-pre-wrap">
                  {selectedItem.raw_content}
                </div>
              </div>

              {/* Media Alt Text if present */}
              {selectedItem.image_alt_text && (
                <div className="space-y-1">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                    Associated Image Alt Text
                  </span>
                  <div className="p-2.5 rounded-lg bg-[#0d1322] border border-[#1f2b42] text-xs text-slate-300 italic">
                    &ldquo;{selectedItem.image_alt_text}&rdquo;
                  </div>
                </div>
              )}

              {/* Compliance Findings Summary */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Automated Engine Findings ({selectedItem.latest_review?.findings_count || 0})
                  </span>
                  <span className="text-[11px] text-slate-500">
                    Mode: {selectedItem.latest_review?.analysis_mode || 'deterministic'}
                  </span>
                </div>

                {(selectedItem.latest_review?.findings || []).length === 0 ? (
                  <div className="p-4 rounded-lg bg-emerald-950/20 border border-emerald-500/30 text-xs text-emerald-300 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>Zero violations detected. Ready for immediate publication approval.</span>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {selectedItem.latest_review?.findings.map((f) => (
                      <div
                        key={f.id}
                        className="p-3 rounded-lg bg-[#141d30] border border-[#22314d] flex items-start justify-between gap-3 text-xs"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <SeverityBadge severity={f.severity} />
                            <span className="font-semibold text-white">{f.title}</span>
                          </div>
                          <p className="text-slate-300">{f.explanation}</p>
                          {f.approved_source && (
                            <div className="text-[11px] text-cyan-400">Source: {f.approved_source}</div>
                          )}
                        </div>

                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#1c2842] text-slate-400 uppercase shrink-0">
                          {f.status}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Reviewer Comments & Feedback */}
              <div className="space-y-2 pt-2 border-t border-[#1f2b42]">
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Reviewer Decision Notes & Feedback
                </label>
                <textarea
                  rows={3}
                  value={reviewerComment}
                  onChange={(e) => setReviewerComment(e.target.value)}
                  placeholder="Provide editorial comments, compliance sign-off notes, or required adjustments..."
                  className="w-full bg-[#162035] border border-[#243350] rounded-lg p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
              </div>

              {/* Critical Violation Warning Banner */}
              {(selectedItem.latest_review?.critical_count ?? 0) > 0 && (
                <div className="p-3.5 rounded-lg bg-red-950/40 border border-red-500/40 text-xs text-red-200 flex items-start gap-2.5">
                  <ShieldAlert className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-red-300">Approval Blocked by Critical Violations</p>
                    <p className="text-red-300/80 mt-0.5">
                      This submission contains unresolved critical compliance violations. Publication approval is disabled until changes are requested or the content is rejected.
                    </p>
                  </div>
                </div>
              )}

              {/* Creator separation of duties note */}
              {userRole === 'creator' && (
                <div className="p-2.5 rounded-lg bg-amber-950/30 border border-amber-500/30 text-xs text-amber-300 flex items-center gap-2">
                  <AlertOctagon className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>Separation of Duties: Creators cannot approve or reject content. Switch to Reviewer mode to take governance actions.</span>
                </div>
              )}

              {/* Decision Action Buttons */}
              <div className="flex flex-wrap items-center justify-end gap-3 pt-2">
                <button
                  onClick={handleReject}
                  disabled={isProcessing || userRole === 'creator'}
                  className="px-4 py-2 rounded-lg bg-rose-950/40 border border-rose-500/40 text-rose-300 font-semibold text-xs hover:bg-rose-900/50 transition-colors flex items-center gap-2 disabled:opacity-50"
                >
                  <XCircle className="w-4 h-4" />
                  <span>Reject Submission</span>
                </button>

                <button
                  onClick={handleRequestChanges}
                  disabled={isProcessing || userRole === 'creator'}
                  className="px-4 py-2 rounded-lg bg-[#1f293d] border border-amber-500/40 text-amber-300 font-semibold text-xs hover:bg-[#283652] transition-colors flex items-center gap-2 disabled:opacity-50"
                >
                  <AlertOctagon className="w-4 h-4" />
                  <span>Request Changes</span>
                </button>

                <button
                  onClick={handleApprove}
                  disabled={isProcessing || (selectedItem.latest_review?.critical_count ?? 0) > 0 || userRole === 'creator'}
                  className="px-5 py-2 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold text-xs hover:from-emerald-400 hover:to-teal-400 transition-all flex items-center gap-2 shadow-lg shadow-emerald-950/40 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Approve Content</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
