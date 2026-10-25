import React from 'react';
import {
  BarChart3,
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  CheckCircle2,
  HelpCircle,
  FileText,
  ShieldAlert
} from 'lucide-react';
import { GovernanceInsights } from '../types';

interface Props {
  insights: GovernanceInsights | null;
}

export const GovernanceInsightsPage: React.FC<Props> = ({ insights }) => {
  const hasData = (insights?.total_reviews_run ?? 0) > 0;

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-bold text-white tracking-tight">Governance Intelligence & Insights</h1>
          <span className="text-xs bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 font-mono px-2 py-0.5 rounded">
            Empirical Data Only
          </span>
        </div>
        <p className="text-sm text-slate-400 mt-1">
          Trend detection, high-friction brand guidelines, recurring nomenclature errors, and policy recommendations.
        </p>
      </div>

      {!hasData ? (
        <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-16 text-center space-y-3">
          <BarChart3 className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">Insufficient Data for Pattern Analysis</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
            BrandGuard AI avoids fabricating statistical projections. Run at least one content compliance review to generate empirical governance insights.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Top High-Level Metrics Summary */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-4">
              <span className="text-xs text-slate-400 uppercase tracking-wider block font-medium">
                Total Evaluated Runs
              </span>
              <div className="text-2xl font-bold text-white mt-1">{insights?.total_reviews_run}</div>
              <span className="text-[11px] text-slate-500">Recorded across all content items</span>
            </div>

            <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-4">
              <span className="text-xs text-slate-400 uppercase tracking-wider block font-medium">
                Findings Intercepted
              </span>
              <div className="text-2xl font-bold text-rose-400 mt-1">
                {insights?.total_findings_detected}
              </div>
              <span className="text-[11px] text-slate-500">Prevented pre-publication violations</span>
            </div>

            <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-4">
              <span className="text-xs text-slate-400 uppercase tracking-wider block font-medium">
                Publish Approval Rate
              </span>
              <div className="text-2xl font-bold text-emerald-400 mt-1">
                {insights && insights.total_content_items > 0
                  ? `${Math.round((insights.approved_count / insights.total_content_items) * 100)}%`
                  : '0%'}
              </div>
              <span className="text-[11px] text-slate-500">
                {insights?.approved_count} of {insights?.total_content_items} approved
              </span>
            </div>

            <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-4">
              <span className="text-xs text-slate-400 uppercase tracking-wider block font-medium">
                Revision Iteration Rate
              </span>
              <div className="text-2xl font-bold text-amber-400 mt-1">
                {insights?.changes_requested_count ?? 0}
              </div>
              <span className="text-[11px] text-slate-500">Returned for creator refinements</span>
            </div>
          </div>

          {/* Two Columns: Category Breakdown & Frequent Mistakes */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Category Breakdown */}
            <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-[#1f2b42] pb-3">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-cyan-400" />
                  <h3 className="font-semibold text-white text-sm">Observed Violation Categories</h3>
                </div>
                <span className="text-xs text-slate-400">Database calculation</span>
              </div>

              <div className="space-y-4">
                {(insights?.category_distribution ?? []).map((cat) => (
                  <div key={cat.category} className="space-y-1 text-xs">
                    <div className="flex justify-between">
                      <span className="font-semibold text-slate-200 capitalize">{cat.category}</span>
                      <span className="text-slate-400">
                        {cat.count} occurrences ({cat.percentage}%)
                      </span>
                    </div>
                    <div className="w-full bg-[#1c263c] h-2.5 rounded-full overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-cyan-500 to-teal-400 h-full rounded-full transition-all duration-500"
                        style={{ width: `${Math.max(cat.percentage, 5)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recurring Brand Mistakes & High Friction Rules */}
            <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-[#1f2b42] pb-3">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <h3 className="font-semibold text-white text-sm">Most Frequent Repeated Mistakes</h3>
                </div>
                <span className="text-xs text-slate-400">Target for creator training</span>
              </div>

              <div className="space-y-3">
                {(insights?.frequent_mistakes ?? []).map((mistake, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg bg-[#141d30] border border-[#22314d] space-y-1 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white">{mistake.issue}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-950 text-amber-300 border border-amber-500/40 font-mono">
                        {mistake.count} times
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-300">
                      <strong className="text-cyan-400">Guidance Recommendation:</strong> {mistake.recommendation}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Actionable Guideline Clarification Suggestions */}
          <div className="bg-[#111827] border border-cyan-500/30 rounded-xl p-5 space-y-4 shadow-sm">
            <div className="flex items-center gap-2 border-b border-[#1f2b42] pb-3">
              <Lightbulb className="w-4 h-4 text-cyan-400" />
              <h3 className="font-semibold text-white text-sm">
                Governance Clarification Suggestions (Empirically Derived)
              </h3>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              Based on the friction points detected during content submissions, consider adjusting the following
              guidelines in the Brand Knowledge Hub:
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
              {(insights?.rule_clarification_suggestions ?? []).map((sugg, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-lg bg-[#141d30] border border-[#243350] text-xs text-slate-300 flex items-start gap-2.5 leading-relaxed"
                >
                  <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                  <span>{sugg}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
