import React, { useState } from 'react';
import {
  FileSearch,
  Upload,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  Send,
  RotateCcw,
  BookOpen,
  HelpCircle,
  Cpu,
  Info
} from 'lucide-react';
import { ContentItem, Brand, Finding, ContentStatus } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';

interface Props {
  brands: Brand[];
  activeBrand: Brand | null;
  onBrandSelect: (brandId: string) => void;
  currentItem: ContentItem | null;
  onItemUpdated: (item: ContentItem) => void;
  onShowToast: (type: 'success' | 'error' | 'info', text: string) => void;
  userRole: 'creator' | 'reviewer';
}

const SAMPLE_PRESETS = [
  {
    label: 'High-Risk Non-Compliant Campaign',
    badge: 'Contains Violations',
    badgeColor: 'bg-red-950 text-red-300 border-red-500/40',
    title: 'Nova Pro Enterprise Security Launch',
    contentType: 'social',
    channel: 'LinkedIn & X / Twitter',
    campaignRef: 'Q1-LAUNCH-CAMPAIGN',
    altText: '', // missing alt text
    content:
      "Get the all-new Nova Pro today for a cheap price of only ₹5,999! Our revolutionary system provides 100% guaranteed results and unbreakable cyber protection. The best in the world for enterprise infrastructure, risk-free!"
  },
  {
    label: 'Fully Compliant Post',
    badge: '100% Compliant',
    badgeColor: 'bg-emerald-950 text-emerald-300 border-emerald-500/40',
    title: 'NovaTech Pro Enterprise Announcement',
    contentType: 'social',
    channel: 'LinkedIn',
    campaignRef: 'Q1-ENTERPRISE-ANNOUNCE',
    altText: 'Executive server workstation running the NovaTech Pro hardware unit with security telemetry dashboard',
    content:
      "Introducing the NovaTech Pro, engineered for resilient enterprise infrastructure. Available now starting at ₹4,999 with a comprehensive 12 months hardware warranty. Experience proactive zero-trust threat management with seamless deployment.\n\nEnterprise security powered by NovaTech. Terms & conditions apply."
  }
];

export const ContentReviewPage: React.FC<Props> = ({
  brands,
  activeBrand,
  onBrandSelect,
  currentItem,
  onItemUpdated,
  onShowToast,
  userRole
}) => {
  // Form State
  const [title, setTitle] = useState(currentItem?.title || '');
  const [contentType, setContentType] = useState(currentItem?.content_type || 'social');
  const [channel, setChannel] = useState(currentItem?.channel || 'LinkedIn');
  const [rawContent, setRawContent] = useState(currentItem?.raw_content || '');
  const [imageAltText, setImageAltText] = useState(currentItem?.image_alt_text || '');
  const [campaignRef, setCampaignRef] = useState(currentItem?.campaign_ref || '');

  // Processing state
  const [isRunningReview, setIsRunningReview] = useState(false);
  const [isSubmittingWorkflow, setIsSubmittingWorkflow] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  // Filters
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  // Dismiss modal state
  const [dismissFindingId, setDismissFindingId] = useState<string | null>(null);
  const [dismissReason, setDismissReason] = useState('');

  // Load preset
  const handleLoadPreset = (preset: typeof SAMPLE_PRESETS[0]) => {
    setTitle(preset.title);
    setContentType(preset.contentType);
    setChannel(preset.channel);
    setCampaignRef(preset.campaignRef);
    setImageAltText(preset.altText);
    setRawContent(preset.content);
    onShowToast('info', `Loaded preset: "${preset.label}"`);
  };

  // Document upload handler
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const res = await api.uploadDocument(file);
      setRawContent(res.content_text);
      if (!title) {
        setTitle(file.name.replace(/\.[^/.]+$/, ''));
      }
      onShowToast('success', `Uploaded document "${res.filename}" (${(res.size_bytes / 1024).toFixed(1)} KB)`);
    } catch (err: any) {
      onShowToast('error', err.message || 'File upload failed');
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  // Run Brand Review
  const handleRunReview = async () => {
    if (!rawContent.trim()) {
      onShowToast('error', 'Please enter content text or upload a document.');
      return;
    }
    if (!title.trim()) {
      onShowToast('error', 'Please provide a content title.');
      return;
    }

    const brandId = activeBrand?.id || 'brand-novatech-001';
    setIsRunningReview(true);

    try {
      const result = await api.createAndReview({
        id: currentItem?.status === 'draft' ? currentItem.id : undefined,
        brand_id: brandId,
        title,
        content_type: contentType,
        channel,
        raw_content: rawContent,
        image_alt_text: imageAltText,
        campaign_ref: campaignRef,
        created_by: `Creator (${userRole})`
      });

      onItemUpdated(result);
      const count = result.latest_review?.findings_count || 0;
      if (count === 0) {
        onShowToast('success', 'Review completed: Content fully complies with all guidelines!');
      } else {
        onShowToast('info', `Review completed: ${count} compliance findings identified.`);
      }
    } catch (err: any) {
      onShowToast('error', err.message || 'Brand review failed.');
    } finally {
      setIsRunningReview(false);
    }
  };

  // Apply Suggestion
  const handleApplySuggestion = async (finding: Finding) => {
    if (!currentItem) return;

    let updatedContent = rawContent;
    // Replace excerpt with recommended correction
    if (finding.excerpt && finding.excerpt !== '[Omitted from submitted copy]' && finding.excerpt !== '[Attached Media / Promotional Image]') {
      updatedContent = updatedContent.replace(finding.excerpt, finding.recommended_correction);
    } else if (finding.category === 'requirements') {
      // Append required phrase
      updatedContent = updatedContent.trim() + finding.recommended_correction;
    }

    setRawContent(updatedContent);

    try {
      // Mark finding applied in DB
      await api.updateFinding(finding.id, 'apply');

      // Create new revision and rerun review
      const revisedItem = await api.reviseContent(currentItem.id, {
        content_text: updatedContent,
        image_alt_text: imageAltText,
        change_summary: `Applied correction: ${finding.title}`,
        actor_name: `Creator (${userRole})`,
        actor_role: userRole
      });

      onItemUpdated(revisedItem);
      onShowToast('success', `Applied correction: "${finding.recommended_correction}". Revision updated!`);
    } catch (err: any) {
      onShowToast('error', err.message || 'Failed to apply suggestion');
    }
  };

  // Dismiss finding
  const handleConfirmDismiss = async () => {
    if (!dismissFindingId || !currentItem) return;

    try {
      await api.updateFinding(dismissFindingId, 'dismiss', dismissReason || 'Dismissed by reviewer');
      // Refetch current item
      const refreshed = await api.getReview(currentItem.id);
      onItemUpdated(refreshed);
      onShowToast('info', 'Finding dismissed.');
      setDismissFindingId(null);
      setDismissReason('');
    } catch (err: any) {
      onShowToast('error', err.message || 'Failed to dismiss finding');
    }
  };

  // Submit for Human Review
  const handleSubmitForReview = async () => {
    if (!currentItem) return;
    setIsSubmittingWorkflow(true);

    try {
      const updated = await api.submitReview(currentItem.id, {
        actor_name: `Creator (${userRole})`,
        actor_role: userRole,
        comments: 'Content ready for brand governance inspection and publication sign-off.'
      });
      onItemUpdated(updated);
      onShowToast('success', 'Content successfully submitted to Review Queue!');
    } catch (err: any) {
      onShowToast('error', err.message || 'Submission failed');
    } finally {
      setIsSubmittingWorkflow(false);
    }
  };

  // Filtered findings
  const findings = currentItem?.latest_review?.findings || [];
  const filteredFindings = findings.filter((f) => {
    if (severityFilter !== 'all' && f.severity !== severityFilter) return false;
    if (categoryFilter !== 'all' && f.category !== categoryFilter) return false;
    return true;
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Content Compliance Review</h1>
          <p className="text-sm text-slate-400 mt-1">
            Analyze copy against brand guidelines, verified pricing, terminology, and legal guardrails.
          </p>
        </div>

        {currentItem && (
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-400 font-mono">Status:</span>
            <StatusBadge status={currentItem.status} />
            <span className="text-xs bg-[#1a253d] border border-[#2d3d5f] text-slate-300 font-mono px-2 py-0.5 rounded">
              Rev #{currentItem.current_revision}
            </span>
          </div>
        )}
      </div>

      {/* Preset Demonstration Buttons */}
      <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Hackathon Quick-Demonstration Presets</span>
          </div>
          <span className="text-[11px] text-slate-400">1-click populated sample copy</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {SAMPLE_PRESETS.map((preset) => (
            <button
              key={preset.label}
              onClick={() => handleLoadPreset(preset)}
              className="text-left p-3 rounded-lg bg-[#141d30] border border-[#243350] hover:border-cyan-500/50 hover:bg-[#18243c] transition-all group"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-white group-hover:text-cyan-300 transition-colors">
                  {preset.label}
                </span>
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${preset.badgeColor}`}>
                  {preset.badge}
                </span>
              </div>
              <p className="text-xs text-slate-400 line-clamp-2">{preset.content}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Two Column Layout: Submission Form (Left) & Review Findings (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Form: 5 Columns */}
        <div className="lg:col-span-5 bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-5 shadow-sm">
          <div className="flex items-center justify-between border-b border-[#1f2b42] pb-3">
            <h2 className="font-semibold text-white text-sm">Content Submission Details</h2>
            <label className="cursor-pointer inline-flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 font-medium bg-[#162035] px-2.5 py-1 rounded border border-[#243350]">
              <Upload className="w-3 h-3" />
              <span>{isUploading ? 'Uploading...' : 'Import .txt / .md'}</span>
              <input
                type="file"
                accept=".txt,.md,.markdown"
                onChange={handleFileUpload}
                disabled={isUploading}
                className="hidden"
              />
            </label>
          </div>

          <div className="space-y-4 text-xs">
            {/* Title */}
            <div>
              <label className="block text-slate-400 font-medium mb-1">Content Title *</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. NovaTech Pro Q1 Launch Post"
                className="w-full bg-[#162035] border border-[#243350] rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-xs"
              />
            </div>

            {/* Brand & Content Type */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Brand Guideline</label>
                <select
                  value={activeBrand?.id || ''}
                  onChange={(e) => onBrandSelect(e.target.value)}
                  className="w-full bg-[#162035] border border-[#243350] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500 text-xs"
                >
                  {brands.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Content Type</label>
                <select
                  value={contentType}
                  onChange={(e) => setContentType(e.target.value)}
                  className="w-full bg-[#162035] border border-[#243350] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500 text-xs capitalize"
                >
                  <option value="social">Social Media Post</option>
                  <option value="marketing">Marketing Copy</option>
                  <option value="website">Website Text</option>
                  <option value="email">Email Campaign</option>
                  <option value="ad">Advertisement</option>
                  <option value="document">Text Document</option>
                </select>
              </div>
            </div>

            {/* Publication Channel */}
            <div>
              <label className="block text-slate-400 font-medium mb-1">Publication Channel</label>
              <input
                type="text"
                value={channel}
                onChange={(e) => setChannel(e.target.value)}
                placeholder="e.g. LinkedIn, X / Twitter, Official Blog"
                className="w-full bg-[#162035] border border-[#243350] rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-xs"
              />
            </div>

            {/* Content Text */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-slate-400 font-medium">Content Copy *</label>
                <span className="text-[11px] text-slate-500 font-mono">
                  {rawContent.length} chars &bull; {rawContent.trim().split(/\s+/).filter(Boolean).length} words
                </span>
              </div>
              <textarea
                rows={6}
                value={rawContent}
                onChange={(e) => setRawContent(e.target.value)}
                placeholder="Enter or paste promotional copy to be evaluated..."
                className="w-full bg-[#162035] border border-[#243350] rounded-lg p-3 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-sans text-xs leading-relaxed"
              />
            </div>

            {/* Image Alt Text (Accessibility check) */}
            <div>
              <label className="block text-slate-400 font-medium mb-1">
                Image Alternative Text <span className="text-slate-500">(Accessibility Check)</span>
              </label>
              <input
                type="text"
                value={imageAltText}
                onChange={(e) => setImageAltText(e.target.value)}
                placeholder="Describe attached promotional visual asset..."
                className="w-full bg-[#162035] border border-[#243350] rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-xs"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="pt-2 space-y-2">
            <button
              onClick={handleRunReview}
              disabled={isRunningReview}
              className="w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950 font-bold text-xs hover:from-cyan-400 hover:to-teal-400 transition-all flex items-center justify-center gap-2 shadow-lg shadow-cyan-950/40 disabled:opacity-50"
            >
              <FileSearch className={`w-4 h-4 ${isRunningReview ? 'animate-spin' : ''}`} />
              <span>{isRunningReview ? 'Running Compliance Engine...' : 'Run Brand Compliance Review'}</span>
            </button>

            {/* Submit to Review Queue if analyzed */}
            {currentItem && currentItem.status === 'draft' && (
              <button
                onClick={handleSubmitForReview}
                disabled={isSubmittingWorkflow}
                className="w-full py-2 px-4 rounded-lg bg-[#18243c] border border-cyan-500/40 text-cyan-300 font-semibold text-xs hover:bg-[#1f2f4e] transition-all flex items-center justify-center gap-2"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Submit for Human Review</span>
              </button>
            )}
          </div>
        </div>

        {/* Right Findings & Results: 7 Columns */}
        <div className="lg:col-span-7 space-y-5">
          {/* Analysis Run Header Bar */}
          <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 shadow-sm">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-[#162035] border border-[#243350] flex items-center justify-center">
                <Cpu className="w-4 h-4 text-cyan-400" />
              </div>
              <div>
                <div className="text-xs font-semibold text-white">
                  Analysis Mode:{' '}
                  <span className="text-cyan-300">
                    {currentItem?.latest_review?.analysis_mode === 'ai_assisted'
                      ? 'AI-Assisted (LLM + Rule Engine)'
                      : 'Deterministic Rule Engine'}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">
                  {currentItem?.latest_review ? `Tested on ${new Date(currentItem.latest_review.created_at).toLocaleTimeString()}` : 'No active review run'}
                </div>
              </div>
            </div>

            {/* Filter pills */}
            {findings.length > 0 && (
              <div className="flex items-center gap-2 text-xs">
                <select
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value)}
                  className="bg-[#162035] border border-[#243350] rounded px-2 py-1 text-slate-300 focus:outline-none text-[11px]"
                >
                  <option value="all">All Severities ({findings.length})</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>

                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="bg-[#162035] border border-[#243350] rounded px-2 py-1 text-slate-300 focus:outline-none text-[11px]"
                >
                  <option value="all">All Categories</option>
                  <option value="terminology">Terminology</option>
                  <option value="facts">Approved Facts</option>
                  <option value="claims">Promotional Claims</option>
                  <option value="tone">Tone</option>
                  <option value="accessibility">Accessibility</option>
                  <option value="requirements">Requirements</option>
                </select>
              </div>
            )}
          </div>

          {/* Findings List or Empty State */}
          {!currentItem?.latest_review ? (
            <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-12 text-center space-y-3">
              <FileSearch className="w-10 h-10 text-slate-600 mx-auto" />
              <h3 className="text-sm font-semibold text-slate-300">No Review Run Yet</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Fill in the content form on the left, load a preset demonstration, and click "Run Brand Compliance Review".
              </p>
            </div>
          ) : findings.length === 0 ? (
            <div className="bg-[#111827] border border-emerald-500/30 rounded-xl p-8 text-center space-y-3 bg-gradient-to-b from-emerald-950/20 to-transparent">
              <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
              <h3 className="text-base font-bold text-white">100% Brand Compliant!</h3>
              <p className="text-xs text-slate-300 max-w-md mx-auto leading-relaxed">
                Zero contradictions found against NovaTech's registered pricing, approved terminology, warranty claims, or mandatory disclaimers.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between text-xs text-slate-400 px-1">
                <span>
                  Showing <strong className="text-white">{filteredFindings.length}</strong> of {findings.length} findings
                </span>
                <span className="text-[11px]">Click "Apply" to insert approved correction</span>
              </div>

              {filteredFindings.map((finding) => {
                const isApplied = finding.status === 'applied';
                const isDismissed = finding.status === 'dismissed';

                return (
                  <div
                    key={finding.id}
                    className={`bg-[#111827] border rounded-xl p-4 space-y-3 transition-all ${
                      isApplied
                        ? 'border-emerald-500/40 bg-emerald-950/10'
                        : isDismissed
                        ? 'border-slate-800 opacity-60'
                        : finding.severity === 'critical'
                        ? 'border-red-500/40'
                        : 'border-[#1f2b42]'
                    }`}
                  >
                    {/* Header: Title, Category, Severity */}
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <SeverityBadge severity={finding.severity} />
                        <span className="text-[11px] font-mono uppercase bg-[#18233a] border border-[#243350] text-cyan-300 px-2 py-0.5 rounded">
                          {finding.category}
                        </span>
                        {/* Evidence Grounding Badge (Round 3) */}
                        <span
                          className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                            finding.evidence_status === 'verified'
                              ? 'bg-emerald-950/70 border-emerald-500/40 text-emerald-300'
                              : finding.evidence_status === 'insufficient_evidence'
                              ? 'bg-amber-950/70 border-amber-500/40 text-amber-300'
                              : 'bg-blue-950/70 border-blue-500/40 text-blue-300'
                          }`}
                        >
                          {finding.evidence_status === 'verified'
                            ? 'Ground-Truth Verified'
                            : finding.evidence_status === 'insufficient_evidence'
                            ? 'Insufficient Evidence (High-Risk Claim)'
                            : 'Policy Advisory'}
                        </span>

                        {isApplied && (
                          <span className="text-[10px] bg-emerald-950 border border-emerald-500/50 text-emerald-300 font-semibold px-2 py-0.5 rounded-full">
                            Applied &check;
                          </span>
                        )}
                        {isDismissed && (
                          <span className="text-[10px] bg-slate-800 border border-slate-700 text-slate-400 px-2 py-0.5 rounded-full">
                            Dismissed
                          </span>
                        )}
                      </div>

                      <span className="text-[11px] text-slate-500 font-mono">
                        Method: {finding.detection_method.replace('_', ' ')}
                      </span>
                    </div>

                    <h4 className="text-sm font-bold text-white">{finding.title}</h4>

                    {/* Excerpt */}
                    {finding.excerpt && (
                      <div className="bg-[#0b101c] border border-[#1b263b] rounded-lg p-2.5 text-xs">
                        <span className="text-slate-500 text-[10px] uppercase font-bold tracking-wider block mb-1">
                          Detected Excerpt:
                        </span>
                        <code className="text-rose-300 font-mono">{finding.excerpt}</code>
                      </div>
                    )}

                    {/* Explanation */}
                    <p className="text-xs text-slate-300 leading-relaxed">{finding.explanation}</p>

                    {/* Applicable Guideline & Traceable Evidence Source (Round 3) */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] bg-[#141d30] p-2.5 rounded-lg border border-[#1f2b42]">
                      <div>
                        <span className="text-slate-400 font-medium block">Applicable Guideline:</span>
                        <span className="text-slate-200">{finding.applicable_guideline}</span>
                      </div>
                      {finding.approved_source && (
                        <div>
                          <span className="text-slate-400 font-medium block">Verified Source Evidence:</span>
                          <span className="text-cyan-400">{finding.approved_source}</span>
                          {finding.evidence_record_id && (
                            <span className="block text-[10px] text-slate-500 font-mono mt-0.5">
                              Record ID: {finding.evidence_record_id}
                            </span>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Suggested Correction & Rationale */}
                    <div className="bg-[#0d1526] border border-cyan-500/30 rounded-lg p-3 space-y-2">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                        <div>
                          <span className="text-[10px] uppercase font-bold text-cyan-400 tracking-wider block mb-0.5">
                            Suggested Correction:
                          </span>
                          <span className="text-xs font-semibold text-emerald-300">
                            {finding.recommended_correction}
                          </span>
                        </div>

                        {!isApplied && !isDismissed && (
                          <div className="flex items-center gap-2 shrink-0">
                            <button
                              onClick={() => handleApplySuggestion(finding)}
                              className="px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition-colors flex items-center gap-1.5 shadow-sm"
                            >
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              <span>Apply Correction</span>
                            </button>
                            <button
                              onClick={() => setDismissFindingId(finding.id)}
                              className="px-2.5 py-1.5 rounded-lg bg-[#18233a] hover:bg-[#202e4d] text-slate-400 hover:text-slate-200 text-xs transition-colors"
                            >
                              Dismiss
                            </button>
                          </div>
                        )}
                      </div>

                      {finding.correction_rationale && (
                        <div className="text-[11px] text-slate-400 pt-1 border-t border-[#1a253a]">
                          <strong className="text-slate-300">Evidence Rationale:</strong> {finding.correction_rationale}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Dismiss Modal */}
      {dismissFindingId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-[#111827] border border-[#1f2b42] rounded-xl max-w-md w-full p-5 space-y-4 shadow-2xl">
            <h3 className="text-sm font-bold text-white">Dismiss Finding with Justification</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Please document why this finding is dismissed to maintain an auditable governance trail.
            </p>
            <textarea
              rows={3}
              value={dismissReason}
              onChange={(e) => setDismissReason(e.target.value)}
              placeholder="e.g. Legal exception granted for partner press release..."
              className="w-full bg-[#162035] border border-[#243350] rounded-lg p-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setDismissFindingId(null)}
                className="px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDismiss}
                className="px-3 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-xs"
              >
                Confirm Dismissal
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
