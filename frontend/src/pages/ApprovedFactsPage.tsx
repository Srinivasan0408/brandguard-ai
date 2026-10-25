import React, { useState } from 'react';
import {
  CheckSquare,
  Plus,
  Trash2,
  Edit,
  ExternalLink,
  ShieldCheck,
  Info,
  Calendar,
  DollarSign
} from 'lucide-react';
import { ApprovedFact, Brand } from '../types';
import { api } from '../services/api';

interface Props {
  facts: ApprovedFact[];
  activeBrand: Brand | null;
  onFactsUpdated: () => void;
  onShowToast: (type: 'success' | 'error' | 'info', text: string) => void;
}

export const ApprovedFactsPage: React.FC<Props> = ({
  facts,
  activeBrand,
  onFactsUpdated,
  onShowToast
}) => {
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingFact, setEditingFact] = useState<ApprovedFact | null>(null);

  // Form fields
  const [productName, setProductName] = useState('');
  const [attribute, setAttribute] = useState('');
  const [approvedValue, setApprovedValue] = useState('');
  const [unitOrCurrency, setUnitOrCurrency] = useState('');
  const [sourceTitle, setSourceTitle] = useState('');
  const [sourceUrl, setSourceUrl] = useState('');
  const [verificationDate, setVerificationDate] = useState(new Date().toISOString().slice(0, 10));

  const [isSaving, setIsSaving] = useState(false);

  const openCreateModal = () => {
    setEditingFact(null);
    setProductName('NovaTech Pro');
    setAttribute('');
    setApprovedValue('');
    setUnitOrCurrency('');
    setSourceTitle('');
    setSourceUrl('');
    setVerificationDate(new Date().toISOString().slice(0, 10));
    setIsModalOpen(true);
  };

  const openEditModal = (fact: ApprovedFact) => {
    setEditingFact(fact);
    setProductName(fact.product_name);
    setAttribute(fact.attribute);
    setApprovedValue(fact.approved_value);
    setUnitOrCurrency(fact.unit_or_currency || '');
    setSourceTitle(fact.source_title);
    setSourceUrl(fact.source_url || '');
    setVerificationDate(fact.verification_date);
    setIsModalOpen(true);
  };

  const handleSaveFact = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!productName || !attribute || !approvedValue || !sourceTitle) {
      onShowToast('error', 'Please fill in all required fields.');
      return;
    }

    setIsSaving(true);
    try {
      const payload = {
        brand_id: activeBrand?.id || 'brand-novatech-001',
        product_name: productName,
        attribute,
        approved_value: approvedValue,
        unit_or_currency: unitOrCurrency,
        source_title: sourceTitle,
        source_url: sourceUrl,
        verification_date: verificationDate,
        status: 'active'
      };

      if (editingFact) {
        await api.updateFact(editingFact.id, payload);
        onShowToast('success', `Updated fact for ${productName} (${attribute})`);
      } else {
        await api.createFact(payload);
        onShowToast('success', `Created approved fact for ${productName} (${attribute})`);
      }

      setIsModalOpen(false);
      onFactsUpdated();
    } catch (err: any) {
      onShowToast('error', err.message || 'Failed to save fact');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteFact = async (factId: string) => {
    if (!confirm('Are you sure you want to delete this approved fact?')) return;
    try {
      await api.deleteFact(factId);
      onShowToast('success', 'Fact removed from registry');
      onFactsUpdated();
    } catch (err: any) {
      onShowToast('error', err.message || 'Failed to delete fact');
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Approved Facts Registry</h1>
            <span className="text-xs bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 font-mono px-2 py-0.5 rounded">
              Verified Ground Truth
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Deterministic ground truth records used to detect incorrect product specifications, pricing, and claims.
          </p>
        </div>

        <button
          onClick={openCreateModal}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950 font-bold text-sm hover:from-cyan-400 hover:to-teal-400 transition-all shadow-lg shadow-cyan-950/40"
        >
          <Plus className="w-4 h-4" />
          <span>Add Approved Fact</span>
        </button>
      </div>

      {/* Ground Truth Disclosure Callout */}
      <div className="bg-[#111c30] border border-cyan-500/30 rounded-xl p-4 flex items-start gap-3 text-xs leading-relaxed">
        <Info className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
        <div className="text-slate-300">
          <strong className="text-white">Deterministic Comparison Engine Disclosure:</strong> BrandGuard AI evaluates
          claims strictly against configured facts in this registry. The system does not claim open-ended web validation,
          ensuring zero hallucinations and verifiable compliance evidence.
        </div>
      </div>

      {/* Facts Table */}
      <div className="bg-[#111827] border border-[#1f2b42] rounded-xl overflow-hidden shadow-sm">
        <div className="p-5 border-b border-[#1f2b42] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <h3 className="font-semibold text-white text-sm">Active Ground Truth Records</h3>
          </div>
          <span className="text-xs text-slate-400">{facts.length} verified facts</span>
        </div>

        {facts.length === 0 ? (
          <div className="p-10 text-center text-slate-500 text-sm">
            No approved facts registered yet. Click &ldquo;Add Approved Fact&rdquo; to configure ground truth.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-[#141d30] text-xs uppercase text-slate-400 tracking-wider">
                <tr>
                  <th className="px-5 py-3 font-medium">Product / Subject</th>
                  <th className="px-5 py-3 font-medium">Attribute</th>
                  <th className="px-5 py-3 font-medium">Approved Value</th>
                  <th className="px-5 py-3 font-medium">Supporting Source</th>
                  <th className="px-5 py-3 font-medium">Verified Date</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                  <th className="px-5 py-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1f2b42]">
                {facts.map((fact) => (
                  <tr key={fact.id} className="hover:bg-[#162035] transition-colors">
                    <td className="px-5 py-4 font-semibold text-white flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-cyan-400" />
                      <span>{fact.product_name}</span>
                    </td>
                    <td className="px-5 py-4 text-xs font-mono text-cyan-300">{fact.attribute}</td>
                    <td className="px-5 py-4 text-xs font-bold text-emerald-300">
                      {fact.approved_value}
                      {fact.unit_or_currency && (
                        <span className="text-[10px] text-slate-400 font-normal ml-1">
                          ({fact.unit_or_currency})
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-4 text-xs text-slate-300 max-w-xs">
                      <div className="truncate font-medium">{fact.source_title}</div>
                      {fact.source_url && (
                        <a
                          href={fact.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-cyan-400 hover:text-cyan-300 text-[11px] inline-flex items-center gap-1 mt-0.5"
                        >
                          <span>Reference Link</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </td>
                    <td className="px-5 py-4 text-xs font-mono text-slate-400">
                      {fact.verification_date}
                    </td>
                    <td className="px-5 py-4">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 uppercase">
                        {fact.status}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => openEditModal(fact)}
                          className="p-1 text-slate-400 hover:text-cyan-400 transition-colors"
                          title="Edit fact"
                        >
                          <Edit className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDeleteFact(fact.id)}
                          className="p-1 text-slate-400 hover:text-rose-400 transition-colors"
                          title="Delete fact"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add / Edit Fact Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-[#111827] border border-[#1f2b42] rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">
              {editingFact ? 'Edit Approved Fact' : 'Register New Approved Fact'}
            </h3>

            <form onSubmit={handleSaveFact} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Product / Subject *</label>
                  <input
                    type="text"
                    required
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    placeholder="e.g. NovaTech Pro"
                    className="w-full bg-[#162035] border border-[#243350] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Attribute *</label>
                  <input
                    type="text"
                    required
                    value={attribute}
                    onChange={(e) => setAttribute(e.target.value)}
                    placeholder="e.g. Price, Warranty, Battery"
                    className="w-full bg-[#162035] border border-[#243350] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Approved Value *</label>
                  <input
                    type="text"
                    required
                    value={approvedValue}
                    onChange={(e) => setApprovedValue(e.target.value)}
                    placeholder="e.g. ₹4,999 or 12 months"
                    className="w-full bg-[#162035] border border-[#243350] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500 font-semibold text-emerald-300"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Unit / Currency</label>
                  <input
                    type="text"
                    value={unitOrCurrency}
                    onChange={(e) => setUnitOrCurrency(e.target.value)}
                    placeholder="e.g. INR (₹), Months, Hours"
                    className="w-full bg-[#162035] border border-[#243350] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Supporting Source Title *</label>
                <input
                  type="text"
                  required
                  value={sourceTitle}
                  onChange={(e) => setSourceTitle(e.target.value)}
                  placeholder="e.g. NovaTech Official Q4 Product Catalog & Pricing Matrix"
                  className="w-full bg-[#162035] border border-[#243350] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Source URL / Reference</label>
                  <input
                    type="text"
                    value={sourceUrl}
                    onChange={(e) => setSourceUrl(e.target.value)}
                    placeholder="https://novatech.internal/catalog/..."
                    className="w-full bg-[#162035] border border-[#243350] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Verification Date *</label>
                  <input
                    type="date"
                    required
                    value={verificationDate}
                    onChange={(e) => setVerificationDate(e.target.value)}
                    className="w-full bg-[#162035] border border-[#243350] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#1f2b42]">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-lg text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSaving}
                  className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold shadow-md disabled:opacity-50"
                >
                  {isSaving ? 'Saving...' : editingFact ? 'Update Fact' : 'Register Fact'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
