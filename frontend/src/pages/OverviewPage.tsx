import React from 'react';
import {
  FileText,
  Clock,
  CheckCircle2,
  AlertOctagon,
  ShieldAlert,
  ArrowRight,
  TrendingUp,
  Sparkles
} from 'lucide-react';
import { GovernanceInsights, ContentItem } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { NavTab } from '../components/Sidebar';

interface Props {
  insights: GovernanceInsights | null;
  recentItems: ContentItem[];
  onNavigate: (tab: NavTab) => void;
  onLoadSample: () => void;
  isLoading: boolean;
}

export const OverviewPage: React.FC<Props> = ({
  insights,
  recentItems,
  onNavigate,
  onLoadSample,
  isLoading
}) => {
  const hasData = (insights?.total_reviews_run ?? 0) > 0 || recentItems.length > 0;

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Brand Governance Overview</h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time compliance analytics, review queue telemetry, and audit metrics.
          </p>
        </div>

        <button
          onClick={() => onNavigate('content_review')}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950 font-semibold text-sm hover:from-cyan-400 hover:to-teal-400 transition-all shadow-lg shadow-cyan-950/40 shrink-0"
        >
          <span>New Content Review</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Onboarding Banner if zero data */}
      {!hasData && !isLoading && (
        <div className="bg-[#131d33] border border-cyan-500/30 rounded-2xl p-6 relative overflow-hidden shadow-xl">
          <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-l from-cyan-500/10 to-transparent pointer-events-none" />
          <div className="max-w-2xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-950 text-cyan-300 border border-cyan-500/30">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Welcome to BrandGuard AI Hackathon MVP</span>
            </div>
            <h2 className="text-xl font-bold text-white">Start your first brand compliance review</h2>
            <p className="text-slate-300 text-sm leading-relaxed">
              Explore how BrandGuard AI catches unapproved pricing, prohibited terms, unsupported guarantees,
              and missing disclosures before publication.
            </p>
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={onLoadSample}
                className="px-4 py-2 rounded-lg bg-cyan-500 text-slate-950 font-semibold text-sm hover:bg-cyan-400 transition-all shadow-md"
              >
                Load Sample Demonstration Post
              </button>
              <button
                onClick={() => onNavigate('brand_guidelines')}
                className="px-4 py-2 rounded-lg bg-[#1a253d] border border-[#2d3d5f] text-slate-200 text-sm hover:bg-[#223150] transition-all"
              >
                Inspect NovaTech Guidelines
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Primary KPI Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Total Reviews */}
        <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Total Reviews</span>
            <FileText className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-white">{insights?.total_reviews_run ?? 0}</div>
          <div className="text-xs text-slate-400 flex items-center gap-1">
            <span className="text-cyan-400 font-medium">{insights?.total_content_items ?? 0}</span> content items created
          </div>
        </div>

        {/* Pending Approval */}
        <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">In Review Queue</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-300">{insights?.pending_approval_count ?? 0}</div>
          <div className="text-xs text-slate-400">Awaiting human reviewer decision</div>
        </div>

        {/* Approved */}
        <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Approved</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-300">{insights?.approved_count ?? 0}</div>
          <div className="text-xs text-slate-400">Ready for safe public release</div>
        </div>

        {/* Changes Requested */}
        <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Revision Needed</span>
            <AlertOctagon className="w-4 h-4 text-orange-400" />
          </div>
          <div className="text-2xl font-bold text-orange-300">{insights?.changes_requested_count ?? 0}</div>
          <div className="text-xs text-slate-400">Returned to creators with feedback</div>
        </div>

        {/* Issues Detected */}
        <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Issues Detected</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold text-rose-300">{insights?.total_findings_detected ?? 0}</div>
          <div className="text-xs text-slate-400">Flagged across all review runs</div>
        </div>
      </div>

      {/* Two Column Layout: Category Distribution & Severity Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Most Frequent Issue Categories */}
        <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-white text-sm flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              <span>Issue Categories Breakdown</span>
            </h3>
            <span className="text-xs text-slate-400">Derived from stored findings</span>
          </div>

          {(insights?.category_distribution ?? []).length === 0 ? (
            <div className="py-8 text-center text-slate-500 text-xs">
              No review findings recorded yet. Run a content review to populate.
            </div>
          ) : (
            <div className="space-y-3">
              {(insights?.category_distribution ?? []).map((cat) => (
                <div key={cat.category} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-300 capitalize font-medium">{cat.category}</span>
                    <span className="text-slate-400">{cat.count} findings ({cat.percentage}%)</span>
                  </div>
                  <div className="w-full bg-[#1c263c] h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-cyan-500 to-teal-400 h-full rounded-full transition-all duration-500"
                      style={{ width: `${Math.max(cat.percentage, 4)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Severity Matrix */}
        <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-white text-sm flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-400" />
              <span>Severity Level Distribution</span>
            </h3>
            <span className="text-xs text-slate-400">Risk classification</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
            {[
              { label: 'Critical', key: 'critical', color: 'border-red-500/40 text-red-400 bg-red-950/30' },
              { label: 'High', key: 'high', color: 'border-orange-500/40 text-orange-400 bg-orange-950/30' },
              { label: 'Medium', key: 'medium', color: 'border-yellow-500/40 text-yellow-400 bg-yellow-950/30' },
              { label: 'Low / Info', key: 'low', color: 'border-blue-500/40 text-blue-400 bg-blue-950/30' }
            ].map((sev) => {
              const count =
                (insights?.severity_distribution ?? []).find(
                  (s) => s.severity.toLowerCase() === sev.key
                )?.count || 0;

              return (
                <div key={sev.label} className={`border rounded-lg p-3 text-center ${sev.color}`}>
                  <div className="text-xs font-medium text-slate-400">{sev.label}</div>
                  <div className="text-xl font-bold mt-1">{count}</div>
                </div>
              );
            })}
          </div>

          <div className="text-xs text-slate-400 bg-[#162035] rounded-lg p-3 border border-[#243350] leading-relaxed">
            <strong className="text-slate-200">Governance Rule:</strong> Critical issues (such as direct pricing mismatches) block automated publishing workflows until verified by an authorized reviewer.
          </div>
        </div>
      </div>

      {/* Recent Activity Table */}
      <div className="bg-[#111827] border border-[#1f2b42] rounded-xl overflow-hidden shadow-sm">
        <div className="p-5 border-b border-[#1f2b42] flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-white text-sm">Recent Content Review Activity</h3>
            <p className="text-xs text-slate-400 mt-0.5">Chronological record of submitted marketing and copy assets</p>
          </div>
          <button
            onClick={() => onNavigate('review_history')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-medium"
          >
            View Full Audit Trail &rarr;
          </button>
        </div>

        {recentItems.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">
            No content reviews in database yet. Click "New Content Review" to start.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-[#141d30] text-xs uppercase text-slate-400 tracking-wider">
                <tr>
                  <th className="px-4 py-3 font-medium">Content Title</th>
                  <th className="px-4 py-3 font-medium">Brand</th>
                  <th className="px-4 py-3 font-medium">Submission Date</th>
                  <th className="px-4 py-3 font-medium">Publication Channel</th>
                  <th className="px-4 py-3 font-medium">Current Status</th>
                  <th className="px-4 py-3 font-medium">Revision</th>
                  <th className="px-4 py-3 font-medium">Last Updated</th>
                  <th className="px-4 py-3 font-medium text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1f2b42]">
                {recentItems.slice(0, 5).map((item) => {
                  const brandName = item.brand_id === 'brand-apex-001' ? 'Apex Global' : 'NovaTech Pro';
                  const submissionDate = new Date(item.created_at).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                  });
                  const updatedDate = new Date(item.updated_at).toLocaleTimeString(undefined, {
                    hour: '2-digit',
                    minute: '2-digit'
                  });

                  return (
                    <tr key={item.id} className="hover:bg-[#162035] transition-colors text-xs">
                      <td className="px-4 py-3.5 font-medium text-white max-w-[200px] truncate">
                        {item.title}
                      </td>
                      <td className="px-4 py-3.5 text-cyan-300 font-medium">
                        {brandName}
                      </td>
                      <td className="px-4 py-3.5 text-slate-400">
                        {submissionDate}
                      </td>
                      <td className="px-4 py-3.5 text-slate-300">
                        {item.channel}
                      </td>
                      <td className="px-4 py-3.5">
                        <StatusBadge status={item.status} />
                      </td>
                      <td className="px-4 py-3.5 font-mono text-slate-400">
                        Rev #{item.current_revision}
                      </td>
                      <td className="px-4 py-3.5 text-slate-400 font-mono">
                        {updatedDate}
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <button
                          onClick={() => onNavigate('content_review')}
                          className="px-2.5 py-1 rounded bg-[#1f2c45] hover:bg-cyan-500/20 hover:text-cyan-300 text-slate-300 font-medium transition-colors"
                        >
                          Inspect
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
