import React, { useState } from 'react';
import {
  BookOpen,
  Plus,
  Trash2,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Save,
  Building2,
  Tag
} from 'lucide-react';
import { Brand } from '../types';
import { api } from '../services/api';

interface Props {
  brand: Brand | null;
  onBrandUpdated: (brand: Brand) => void;
  onShowToast: (type: 'success' | 'error' | 'info', text: string) => void;
}

export const BrandGuidelinesPage: React.FC<Props> = ({
  brand,
  onBrandUpdated,
  onShowToast
}) => {
  if (!brand) {
    return (
      <div className="py-12 text-center text-slate-500 text-sm">
        No brand configured. Select or create a brand.
      </div>
    );
  }

  // Local state for editing
  const [preferredTone, setPreferredTone] = useState(brand.preferred_tone);
  const [targetAudience, setTargetAudience] = useState(brand.target_audience);
  const [approvedTerms, setApprovedTerms] = useState<string[]>(brand.approved_terminology || []);
  const [prohibitedTerms, setProhibitedTerms] = useState<string[]>(brand.prohibited_terminology || []);
  const [requiredPhrases, setRequiredPhrases] = useState<string[]>(brand.required_phrases || []);
  const [styleGuidelines, setStyleGuidelines] = useState<string[]>(brand.style_guidelines || []);

  const [newApprovedTerm, setNewApprovedTerm] = useState('');
  const [newProhibitedTerm, setNewProhibitedTerm] = useState('');
  const [newRequiredPhrase, setNewRequiredPhrase] = useState('');
  const [newStyleGuideline, setNewStyleGuideline] = useState('');

  const [isSaving, setIsSaving] = useState(false);

  // Term helpers
  const addApprovedTerm = () => {
    if (!newApprovedTerm.trim()) return;
    if (approvedTerms.includes(newApprovedTerm.trim())) return;
    setApprovedTerms([...approvedTerms, newApprovedTerm.trim()]);
    setNewApprovedTerm('');
  };

  const removeApprovedTerm = (term: string) => {
    setApprovedTerms(approvedTerms.filter((t) => t !== term));
  };

  const addProhibitedTerm = () => {
    if (!newProhibitedTerm.trim()) return;
    if (prohibitedTerms.includes(newProhibitedTerm.trim())) return;
    setProhibitedTerms([...prohibitedTerms, newProhibitedTerm.trim()]);
    setNewProhibitedTerm('');
  };

  const removeProhibitedTerm = (term: string) => {
    setProhibitedTerms(prohibitedTerms.filter((t) => t !== term));
  };

  const addRequiredPhrase = () => {
    if (!newRequiredPhrase.trim()) return;
    setRequiredPhrases([...requiredPhrases, newRequiredPhrase.trim()]);
    setNewRequiredPhrase('');
  };

  const removeRequiredPhrase = (phrase: string) => {
    setRequiredPhrases(requiredPhrases.filter((p) => p !== phrase));
  };

  const addStyleGuideline = () => {
    if (!newStyleGuideline.trim()) return;
    setStyleGuidelines([...styleGuidelines, newStyleGuideline.trim()]);
    setNewStyleGuideline('');
  };

  const removeStyleGuideline = (item: string) => {
    setStyleGuidelines(styleGuidelines.filter((g) => g !== item));
  };

  // Save changes
  const handleSave = async () => {
    setIsSaving(true);
    try {
      const updated = await api.updateBrand(brand.id, {
        preferred_tone: preferredTone,
        target_audience: targetAudience,
        approved_terminology: approvedTerms,
        prohibited_terminology: prohibitedTerms,
        required_phrases: requiredPhrases,
        style_guidelines: styleGuidelines,
      });
      onBrandUpdated(updated);
      onShowToast('success', 'Brand guidelines saved to database successfully!');
    } catch (err: any) {
      onShowToast('error', err.message || 'Failed to save brand guidelines');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Brand Knowledge Hub</h1>
            <span className="text-xs bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 font-mono px-2 py-0.5 rounded">
              {brand.name}
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Configure tone, approved nomenclature, prohibited marketing buzzwords, and mandatory disclaimers.
          </p>
        </div>

        <button
          onClick={handleSave}
          disabled={isSaving}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950 font-bold text-sm hover:from-cyan-400 hover:to-teal-400 transition-all shadow-lg shadow-cyan-950/40 disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          <span>{isSaving ? 'Saving...' : 'Save Guidelines'}</span>
        </button>
      </div>

      {/* Two Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Brand Identity & Tone */}
        <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-5">
          <div className="flex items-center gap-2 border-b border-[#1f2b42] pb-3">
            <Building2 className="w-4 h-4 text-cyan-400" />
            <h2 className="font-semibold text-white text-sm">Brand Voice & Persona</h2>
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-400 font-medium mb-1">Brand Description</label>
              <div className="p-3 rounded-lg bg-[#162035] border border-[#243350] text-slate-300 text-xs leading-relaxed">
                {brand.description}
              </div>
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">Target Audience</label>
              <input
                type="text"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                className="w-full bg-[#162035] border border-[#243350] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500 text-xs"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">
                Preferred Brand Tone & Style Voice
              </label>
              <textarea
                rows={3}
                value={preferredTone}
                onChange={(e) => setPreferredTone(e.target.value)}
                className="w-full bg-[#162035] border border-[#243350] rounded-lg p-3 text-white focus:outline-none focus:border-cyan-500 text-xs leading-relaxed"
              />
              <p className="text-[11px] text-slate-500 mt-1">
                Used by the rule engine and optional AI assistant to evaluate tonal composure and hype levels.
              </p>
            </div>
          </div>
        </div>

        {/* Right: Mandatory Legal Disclaimers & Required Phrases */}
        <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 border-b border-[#1f2b42] pb-3">
            <BookOpen className="w-4 h-4 text-teal-400" />
            <h2 className="font-semibold text-white text-sm">Mandatory Disclaimers & Phrases</h2>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={newRequiredPhrase}
                onChange={(e) => setNewRequiredPhrase(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addRequiredPhrase()}
                placeholder="Add required disclaimer or phrase..."
                className="flex-1 bg-[#162035] border border-[#243350] rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
              />
              <button
                onClick={addRequiredPhrase}
                className="px-3 py-1.5 rounded-lg bg-teal-500 hover:bg-teal-400 text-slate-950 font-semibold text-xs flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add</span>
              </button>
            </div>

            <div className="space-y-2">
              {requiredPhrases.map((phrase) => (
                <div
                  key={phrase}
                  className="flex items-center justify-between p-2.5 rounded-lg bg-[#141d30] border border-[#22314d] text-xs text-slate-200"
                >
                  <span className="font-medium truncate pr-2">&ldquo;{phrase}&rdquo;</span>
                  <button
                    onClick={() => removeRequiredPhrase(phrase)}
                    className="text-slate-500 hover:text-rose-400 transition-colors p-1"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Terminology Registers: Approved vs Prohibited */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Approved Terminology */}
        <div className="bg-[#111827] border border-emerald-500/30 rounded-xl p-5 space-y-4 shadow-sm">
          <div className="flex items-center justify-between border-b border-[#1f2b42] pb-3">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <h3 className="font-semibold text-white text-sm">Approved Terminology & Registered Names</h3>
            </div>
            <span className="text-[11px] text-slate-400">{approvedTerms.length} terms</span>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="text"
              value={newApprovedTerm}
              onChange={(e) => setNewApprovedTerm(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addApprovedTerm()}
              placeholder="e.g. NovaTech Pro, QuantumSync..."
              className="flex-1 bg-[#162035] border border-[#243350] rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
            />
            <button
              onClick={addApprovedTerm}
              className="px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add</span>
            </button>
          </div>

          <div className="flex flex-wrap gap-2 pt-1">
            {approvedTerms.map((term) => (
              <span
                key={term}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950/60 border border-emerald-500/40 text-emerald-300"
              >
                <span>{term}</span>
                <button
                  onClick={() => removeApprovedTerm(term)}
                  className="hover:text-white transition-colors"
                >
                  &times;
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Prohibited Terminology */}
        <div className="bg-[#111827] border border-red-500/30 rounded-xl p-5 space-y-4 shadow-sm">
          <div className="flex items-center justify-between border-b border-[#1f2b42] pb-3">
            <div className="flex items-center gap-2">
              <XCircle className="w-4 h-4 text-rose-400" />
              <h3 className="font-semibold text-white text-sm">Prohibited Terminology & High-Risk Buzzwords</h3>
            </div>
            <span className="text-[11px] text-slate-400">{prohibitedTerms.length} prohibited</span>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="text"
              value={newProhibitedTerm}
              onChange={(e) => setNewProhibitedTerm(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addProhibitedTerm()}
              placeholder="e.g. cheap, unbreakable, foolproof..."
              className="flex-1 bg-[#162035] border border-[#243350] rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-rose-500"
            />
            <button
              onClick={addProhibitedTerm}
              className="px-3 py-1.5 rounded-lg bg-rose-500 hover:bg-rose-400 text-slate-950 font-semibold text-xs flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add</span>
            </button>
          </div>

          <div className="flex flex-wrap gap-2 pt-1">
            {prohibitedTerms.map((term) => (
              <span
                key={term}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-950/60 border border-red-500/40 text-red-300"
              >
                <span>{term}</span>
                <button
                  onClick={() => removeProhibitedTerm(term)}
                  className="hover:text-white transition-colors"
                >
                  &times;
                </button>
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Style Guidelines List */}
      <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-[#1f2b42] pb-3">
          <h3 className="font-semibold text-white text-sm">Configured Editorial & Governance Rules</h3>
          <span className="text-xs text-slate-400">{styleGuidelines.length} active rules</span>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="text"
            value={newStyleGuideline}
            onChange={(e) => setNewStyleGuideline(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && addStyleGuideline()}
            placeholder="Add new editorial or compliance rule..."
            className="flex-1 bg-[#162035] border border-[#243350] rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
          />
          <button
            onClick={addStyleGuideline}
            className="px-3 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-xs flex items-center gap-1"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Rule</span>
          </button>
        </div>

        <div className="divide-y divide-[#1f2b42] pt-1">
          {styleGuidelines.map((rule, idx) => (
            <div key={idx} className="py-2.5 flex items-center justify-between text-xs text-slate-300">
              <span className="pr-4 leading-relaxed">&bull; {rule}</span>
              <button
                onClick={() => removeStyleGuideline(rule)}
                className="text-slate-500 hover:text-rose-400 transition-colors p-1"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
