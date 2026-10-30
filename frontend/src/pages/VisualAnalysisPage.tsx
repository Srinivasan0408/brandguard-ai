import React, { useState } from 'react';
import {
  Upload,
  Palette,
  Eye,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  Sparkles,
  Info,
  Maximize2,
  FileText
} from 'lucide-react';
import { Brand, VisualAnalysisResponse } from '../types';
import { api } from '../services/api';

interface Props {
  activeBrand: Brand | null;
  onShowToast: (type: 'success' | 'error' | 'info', text: string) => void;
}

export const VisualAnalysisPage: React.FC<Props> = ({ activeBrand, onShowToast }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [altText, setAltText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<VisualAnalysisResponse | null>(null);

  // Generate synthetic sample brand image for 1-click test
  const handleLoadSampleAsset = () => {
    // Create a 800x500 canvas with NovaTech primary brand cyan (#06b6d4) and slate (#0f172a)
    const canvas = document.createElement('canvas');
    canvas.width = 1000;
    canvas.height = 600;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      // Dark slate background
      ctx.fillStyle = '#0f172a';
      ctx.fillRect(0, 0, 1000, 600);

      // Cyan accent card
      ctx.fillStyle = '#06b6d4';
      ctx.fillRect(80, 80, 840, 240);

      // Brand text
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 36px sans-serif';
      ctx.fillText('NovaTech Pro — Enterprise Zero Trust Server', 120, 210);

      // Secondary teal footer
      ctx.fillStyle = '#14b8a6';
      ctx.fillRect(80, 360, 400, 160);
      ctx.fillStyle = '#ffffff';
      ctx.font = '24px sans-serif';
      ctx.fillText('12 Months Warranty Included', 110, 450);

      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'novatech_pro_launch_banner.png', { type: 'image/png' });
          setSelectedFile(file);
          setImagePreview(canvas.toDataURL());
          setAltText('Executive launch banner for NovaTech Pro server showing zero trust capabilities and warranty');
          onShowToast('info', 'Loaded synthetic NovaTech enterprise launch asset');
        }
      }, 'image/png');
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onload = (event) => {
        setImagePreview(event.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      onShowToast('error', 'Please upload or select an image asset to analyze.');
      return;
    }
    setIsAnalyzing(true);
    try {
      const brandId = activeBrand?.id || 'brand-novatech-001';
      const analysis = await api.analyzeVisualAsset(selectedFile, brandId, altText);
      setResult(analysis);
      onShowToast('success', `Visual brand analysis completed for "${analysis.file_name}"!`);
    } catch (err: any) {
      onShowToast('error', err.message || 'Visual analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Visual Brand & Accessibility Analysis</h1>
            <span className="text-xs bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 font-mono px-2 py-0.5 rounded">
              Round 3 Capability
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Deterministic color palette harmonization, WCAG 2.2 contrast evaluation, dimension checks, and alt-text verification.
          </p>
        </div>

        <button
          onClick={handleLoadSampleAsset}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#162035] border border-[#243350] hover:border-cyan-500/50 hover:bg-[#1a2640] text-cyan-300 text-xs font-semibold transition-all shadow-sm shrink-0"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Load Sample Brand Banner</span>
        </button>
      </div>

      {/* Main Grid: Upload & Controls (Left 5 Cols) vs Results & Telemetry (Right 7 Cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Image Upload & Config */}
        <div className="lg:col-span-5 bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-5 shadow-sm">
          <div className="flex items-center justify-between border-b border-[#1f2b42] pb-3">
            <h2 className="font-semibold text-white text-sm flex items-center gap-2">
              <Upload className="w-4 h-4 text-cyan-400" />
              <span>Asset Upload & Metadata</span>
            </h2>
            <span className="text-[11px] text-slate-400 font-mono">PNG, JPG, WEBP &bull; Max 5MB</span>
          </div>

          {/* Upload Dropzone */}
          <div className="space-y-3">
            <label className="block border-2 border-dashed border-[#243350] hover:border-cyan-500/60 bg-[#0d1322] rounded-xl p-6 text-center cursor-pointer transition-colors group">
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                onChange={handleFileChange}
                className="hidden"
              />
              {imagePreview ? (
                <div className="space-y-3">
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="max-h-48 mx-auto rounded-lg object-contain shadow-md border border-[#1f2b42]"
                  />
                  <span className="text-xs text-cyan-400 font-medium block group-hover:underline">
                    Click to replace {selectedFile?.name}
                  </span>
                </div>
              ) : (
                <div className="space-y-2 py-4">
                  <Palette className="w-10 h-10 text-slate-500 mx-auto group-hover:text-cyan-400 transition-colors" />
                  <div className="text-xs font-medium text-slate-200">
                    Click or drop visual brand asset here
                  </div>
                  <div className="text-[11px] text-slate-500">
                    Marketing banners, social cards, packaging graphics
                  </div>
                </div>
              )}
            </label>
          </div>

          {/* Associated Alternative Text (Accessibility) */}
          <div className="space-y-1.5 text-xs">
            <label className="block text-slate-300 font-medium">
              Associated Alternative Text (Accessibility Review)
            </label>
            <textarea
              rows={3}
              value={altText}
              onChange={(e) => setAltText(e.target.value)}
              placeholder="Provide the screen-reader caption for this visual asset..."
              className="w-full bg-[#162035] border border-[#243350] rounded-lg p-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 leading-relaxed"
            />
            <span className="text-[10px] text-slate-500">
              Evaluated against WCAG 2.2 AA non-text digital asset inclusion criteria.
            </span>
          </div>

          {/* Brand Reference Palette */}
          <div className="bg-[#141d30] border border-[#22314d] rounded-lg p-3 text-xs space-y-2">
            <div className="flex justify-between items-center text-slate-400">
              <span className="font-medium text-white">{activeBrand?.name || 'NovaTech'} Target Palette</span>
              <span className="text-[10px] font-mono">Configured</span>
            </div>
            <div className="flex items-center gap-2">
              {['#06b6d4', '#14b8a6', '#0f172a', '#1e293b', '#ffffff'].map((color) => (
                <div key={color} className="flex flex-col items-center gap-1">
                  <div
                    className="w-6 h-6 rounded-md border border-white/20 shadow-sm"
                    style={{ backgroundColor: color }}
                    title={color}
                  />
                  <span className="text-[9px] font-mono text-slate-400">{color}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Run Button */}
          <button
            onClick={handleAnalyze}
            disabled={!selectedFile || isAnalyzing}
            className="w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950 font-bold text-xs hover:from-cyan-400 hover:to-teal-400 transition-all flex items-center justify-center gap-2 shadow-lg shadow-cyan-950/40 disabled:opacity-50"
          >
            <Eye className={`w-4 h-4 ${isAnalyzing ? 'animate-spin' : ''}`} />
            <span>{isAnalyzing ? 'Extracting & Comparing Pixels...' : 'Run Visual Consistency Analysis'}</span>
          </button>
        </div>

        {/* Right Column: Analysis Results */}
        <div className="lg:col-span-7 space-y-5">
          {!result ? (
            <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-16 text-center space-y-3">
              <Palette className="w-12 h-12 text-slate-600 mx-auto" />
              <h3 className="text-sm font-semibold text-slate-300">No Visual Analysis Executed Yet</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto leading-relaxed">
                Upload a marketing banner or click &ldquo;Load Sample Brand Banner&rdquo; to test automated palette matching,
                WCAG 2.2 contrast validation, and resolution integrity.
              </p>
            </div>
          ) : (
            <div className="space-y-5 animate-in fade-in duration-200">
              {/* Summary KPIs */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {/* Palette Match */}
                <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-4 space-y-1">
                  <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider block">
                    Brand Palette Match
                  </span>
                  <div className="text-2xl font-bold text-cyan-300">
                    {result.palette_compliance_score}%
                  </div>
                  <span className="text-[10px] text-slate-500">Surface tone harmony</span>
                </div>

                {/* Contrast Ratio */}
                <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-4 space-y-1">
                  <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider block">
                    Contrast Separation
                  </span>
                  <div className={`text-2xl font-bold ${result.wcag_aa_compliant ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {result.contrast_ratio ? `${result.contrast_ratio}:1` : 'N/A'}
                  </div>
                  <span className="text-[10px] text-slate-500">
                    {result.wcag_aa_compliant ? 'WCAG 2.2 AA Pass' : 'Under 4.5:1 Target'}
                  </span>
                </div>

                {/* Dimensions */}
                <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-4 space-y-1">
                  <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider block">
                    Resolution
                  </span>
                  <div className="text-2xl font-bold text-white font-mono">
                    {result.dimensions.width}&times;{result.dimensions.height}
                  </div>
                  <span className="text-[10px] text-slate-500">{result.format} &bull; {(result.file_size_bytes / 1024).toFixed(0)} KB</span>
                </div>
              </div>

              {/* Dominant Color Swatches */}
              <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-white text-xs uppercase tracking-wider">
                    Extracted Dominant Color Clusters
                  </h3>
                  <span className="text-[11px] text-slate-400">Quantized pixel histogram</span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-1">
                  {result.dominant_colors.map((c, i) => (
                    <div
                      key={i}
                      className="bg-[#141d30] border border-[#22314d] rounded-lg p-2.5 text-center space-y-1.5"
                    >
                      <div
                        className="w-full h-10 rounded border border-white/10 shadow-inner"
                        style={{ backgroundColor: c.hex }}
                      />
                      <div className="font-mono text-xs font-semibold text-slate-200">{c.hex}</div>
                      <div className="text-[10px] text-slate-400">{c.percentage}% of pixels</div>
                      <span
                        className={`inline-block text-[9px] font-semibold px-1.5 py-0.5 rounded-full border ${
                          c.is_brand_match
                            ? 'bg-emerald-950 text-emerald-300 border-emerald-500/40'
                            : 'bg-slate-800 text-slate-400 border-slate-700'
                        }`}
                      >
                        {c.is_brand_match ? 'Brand Match' : 'Neutral/Other'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* OCR Canvas Text Extraction & Governance Section */}
              <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-[#1f2b42] pb-3">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-cyan-400" />
                    <h3 className="font-semibold text-white text-xs uppercase tracking-wider">
                      OCR Canvas Text & Brand Rule Review
                    </h3>
                  </div>
                  {result.ocr_available ? (
                    <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-500/40">
                      OCR Active ({result.ocr_confidence ?? 0}% Confidence)
                    </span>
                  ) : (
                    <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                      Fallback Mode Active
                    </span>
                  )}
                </div>

                {result.ocr_available ? (
                  <div className="space-y-3">
                    <div>
                      <span className="text-[11px] text-slate-400 font-medium block mb-1">
                        Extracted Canvas Text Snippets:
                      </span>
                      <div className="bg-[#0c1220] border border-[#1b263b] rounded-lg p-3 text-xs font-mono text-cyan-200 break-words leading-relaxed max-h-32 overflow-y-auto">
                        {result.extracted_text || <span className="text-slate-500 italic">No readable text detected in image canvas</span>}
                      </div>
                    </div>

                    {result.ocr_findings && result.ocr_findings.length > 0 ? (
                      <div className="space-y-2 pt-1">
                        <span className="text-[11px] font-semibold text-rose-300 flex items-center gap-1.5">
                          <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                          <span>Identified Brand Violations in Graphic Canvas ({result.ocr_findings.length}):</span>
                        </span>
                        {result.ocr_findings.map((f, fIdx) => (
                          <div
                            key={fIdx}
                            className="bg-rose-950/20 border border-rose-500/30 rounded-lg p-3 text-xs space-y-1.5"
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-white text-xs">{f.title}</span>
                              <span className="text-[9px] font-semibold uppercase px-1.5 py-0.5 rounded-full bg-rose-900/60 text-rose-300 border border-rose-500/40">
                                {f.severity}
                              </span>
                            </div>
                            <div className="text-[11px] text-slate-300 leading-relaxed">
                              {f.explanation}
                            </div>
                            <div className="bg-[#090f1d] p-2 rounded border border-rose-900/40 text-[10px] space-y-1">
                              <div>
                                <span className="text-slate-500">Trigger Match: </span>
                                <span className="font-mono text-rose-300 font-bold">&ldquo;{f.trigger_text}&rdquo;</span>
                              </div>
                              <div>
                                <span className="text-slate-500">Applicable Guideline: </span>
                                <span className="text-slate-300">{f.applicable_guideline}</span>
                              </div>
                              <div className="text-emerald-400 pt-0.5">
                                <span className="text-slate-400">Suggested Correction: </span>
                                {f.recommended_correction}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="bg-emerald-950/20 border border-emerald-500/30 rounded-lg p-2.5 text-xs flex items-center gap-2 text-emerald-300">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        <span>Canvas text conforms to approved brand terminology. Zero prohibited terms detected.</span>
                      </div>
                    )}

                    {result.ocr_status_note && (
                      <div className="text-[10px] text-slate-500 flex items-center gap-1 italic">
                        <Info className="w-3 h-3 text-slate-400 shrink-0" />
                        <span>{result.ocr_status_note}</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="bg-[#141d30] border border-[#22314d] rounded-lg p-3 text-xs space-y-2">
                    <p className="text-slate-300 leading-relaxed">
                      {result.ocr_status_note || "Tesseract OCR binary not detected in runtime environment; visual color, contrast, and resolution analysis running 100% deterministically."}
                    </p>
                    <div className="text-[10px] text-slate-400 flex items-center gap-1.5 italic">
                      <Info className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                      <span>Color palette harmony, WCAG 2.2 AA tonal contrast, and resolution integrity are verified deterministically.</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Check Findings List */}
              <div className="bg-[#111827] border border-[#1f2b42] rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-[#1f2b42] pb-3">
                  <h3 className="font-semibold text-white text-sm">Automated Visual & Accessibility Checks</h3>
                  <span className="text-xs text-slate-400">{result.checks.length} criteria evaluated</span>
                </div>

                <div className="space-y-3">
                  {result.checks.map((chk, idx) => {
                    const isPass = chk.status === 'pass';
                    const isFail = chk.status === 'fail';

                    return (
                      <div
                        key={idx}
                        className={`p-3.5 rounded-lg border text-xs space-y-2 ${
                          isPass
                            ? 'bg-[#141f33] border-emerald-500/30'
                            : isFail
                            ? 'bg-red-950/20 border-red-500/40'
                            : 'bg-amber-950/20 border-amber-500/40'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {isPass ? (
                              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                            ) : isFail ? (
                              <XCircle className="w-4 h-4 text-rose-400" />
                            ) : (
                              <AlertTriangle className="w-4 h-4 text-amber-400" />
                            )}
                            <span className="font-bold text-white text-xs">{chk.check_name}</span>
                          </div>

                          <span
                            className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full border ${
                              isPass
                                ? 'bg-emerald-950 text-emerald-300 border-emerald-500/40'
                                : isFail
                                ? 'bg-red-950 text-red-300 border-red-500/40'
                                : 'bg-amber-950 text-amber-300 border-amber-500/40'
                            }`}
                          >
                            {chk.status}
                          </span>
                        </div>

                        <p className="text-slate-300 leading-relaxed">{chk.explanation}</p>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] bg-[#0d1322] p-2 rounded border border-[#1b263b]">
                          <div>
                            <span className="text-slate-500 block">Observed:</span>
                            <span className="text-slate-200 font-mono">{chk.observed_value}</span>
                          </div>
                          <div>
                            <span className="text-slate-500 block">Expected:</span>
                            <span className="text-cyan-300 font-mono">{chk.expected_value}</span>
                          </div>
                        </div>

                        {!isPass && (
                          <div className="text-[11px] text-amber-300 bg-amber-950/30 p-2 rounded border border-amber-500/20">
                            <strong>Recommended Fix:</strong> {chk.recommended_fix}
                          </div>
                        )}

                        {chk.uncertainty_note && (
                          <div className="text-[10px] text-slate-500 flex items-center gap-1 italic">
                            <Info className="w-3 h-3 text-slate-400" />
                            <span>{chk.uncertainty_note}</span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
