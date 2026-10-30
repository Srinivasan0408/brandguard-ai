import React from 'react';
import {
  LayoutDashboard,
  FileSearch,
  BookOpen,
  CheckSquare,
  Palette,
  Inbox,
  History,
  BarChart3,
  Settings,
  Building2
} from 'lucide-react';

export type NavTab =
  | 'overview'
  | 'content_review'
  | 'visual_analysis'
  | 'brand_guidelines'
  | 'approved_facts'
  | 'review_queue'
  | 'review_history'
  | 'governance_insights'
  | 'settings';

interface Props {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  pendingCount?: number;
  brandName?: string;
}

export const Sidebar: React.FC<Props> = ({
  activeTab,
  onTabChange,
  pendingCount = 0,
  brandName = 'NovaTech'
}) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'content_review', label: 'Content Review', icon: FileSearch },
    { id: 'visual_analysis', label: 'Visual Analysis', icon: Palette },
    { id: 'brand_guidelines', label: 'Brand Guidelines', icon: BookOpen },
    { id: 'approved_facts', label: 'Approved Facts', icon: CheckSquare },
    {
      id: 'review_queue',
      label: 'Review Queue',
      icon: Inbox,
      badge: pendingCount > 0 ? pendingCount : undefined
    },
    { id: 'review_history', label: 'Review History', icon: History },
    { id: 'governance_insights', label: 'Governance Insights', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#0d1322] border-r border-[#1f2b42] flex flex-col justify-between shrink-0 select-none">
      <div className="p-4 space-y-6">
        {/* Active Brand Card */}
        <div className="bg-[#141d30] border border-[#22314d] rounded-xl p-3 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-cyan-950/70 border border-cyan-500/40 flex items-center justify-center shrink-0">
            <Building2 className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="overflow-hidden">
            <div className="text-xs text-slate-400 font-medium uppercase tracking-wider">Active Brand</div>
            <div className="text-sm font-semibold text-white truncate">{brandName}</div>
          </div>
        </div>

        {/* Navigation List */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id as NavTab)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-950/70 to-slate-800 text-cyan-300 border-l-4 border-cyan-400 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-[#162035]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge !== undefined && (
                  <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-[#1a253a] text-xs text-slate-500">
        <p className="font-medium text-slate-400">TechCircuit Hackathon</p>
        <p>Round 3 – Final Build &bull; Team TECHSPARKZ</p>
      </div>
    </aside>
  );
};
