import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar, NavTab } from './components/Sidebar';
import { ToastContainer, ToastMessage } from './components/Toast';

import { OverviewPage } from './pages/OverviewPage';
import { ContentReviewPage } from './pages/ContentReviewPage';
import { BrandGuidelinesPage } from './pages/BrandGuidelinesPage';
import { ApprovedFactsPage } from './pages/ApprovedFactsPage';
import { ReviewQueuePage } from './pages/ReviewQueuePage';
import { ReviewHistoryPage } from './pages/ReviewHistoryPage';
import { GovernanceInsightsPage } from './pages/GovernanceInsightsPage';
import { SettingsPage } from './pages/SettingsPage';

import { Brand, ApprovedFact, ContentItem, GovernanceInsights, HealthStatus } from './types';
import { api } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState<NavTab>('overview');
  const [userRole, setUserRole] = useState<'creator' | 'reviewer'>('creator');
  const [health, setHealth] = useState<HealthStatus | null>(null);

  const [brands, setBrands] = useState<Brand[]>([]);
  const [activeBrand, setActiveBrand] = useState<Brand | null>(null);
  const [facts, setFacts] = useState<ApprovedFact[]>([]);
  const [contentItems, setContentItems] = useState<ContentItem[]>([]);
  const [currentItem, setCurrentItem] = useState<ContentItem | null>(null);
  const [insights, setInsights] = useState<GovernanceInsights | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  // Add toast helper
  const showToast = useCallback((type: 'success' | 'error' | 'info', text: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, text }]);
  }, []);

  const dismissToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // Load initial data
  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      // 1. Health
      try {
        const h = await api.getHealth();
        setHealth(h);
      } catch {
        // Backend might be offline or spinning up
      }

      // 2. Brands
      const bList = await api.getBrands();
      setBrands(bList);
      if (bList.length > 0) {
        setActiveBrand((prev) => prev || bList[0]);
      }

      // 3. Facts
      const fList = await api.getFacts();
      setFacts(fList);

      // 4. Content Items
      const cList = await api.getReviews();
      setContentItems(cList);
      if (cList.length > 0) {
        setCurrentItem((prev) => prev || cList[0]);
      }

      // 5. Insights
      const ins = await api.getInsights();
      setInsights(ins);
    } catch (err: any) {
      console.error('Data load error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Brand selection
  const handleBrandSelect = (brandId: string) => {
    const found = brands.find((b) => b.id === brandId);
    if (found) setActiveBrand(found);
  };

  // Reset Demo
  const handleResetDemo = async () => {
    setIsResetting(true);
    try {
      await api.resetDemo();
      await loadData();
      showToast('success', 'Demonstration database reset to NovaTech defaults.');
    } catch (err: any) {
      showToast('error', err.message || 'Failed to reset demo data');
    } finally {
      setIsResetting(false);
    }
  };

  // Overview quick-action: Load Sample Review
  const handleLoadSampleReview = async () => {
    setActiveTab('content_review');
    try {
      const res = await api.createAndReview({
        brand_id: activeBrand?.id || 'brand-novatech-001',
        title: 'Nova Pro Enterprise Security Launch',
        content_type: 'social',
        channel: 'LinkedIn & X / Twitter',
        campaign_ref: 'Q1-LAUNCH-CAMPAIGN',
        image_alt_text: '',
        raw_content:
          "Get the all-new Nova Pro today for a cheap price of only ₹5,999! Our revolutionary system provides 100% guaranteed results and unbreakable cyber protection. The best in the world for enterprise infrastructure, risk-free!",
        created_by: 'Creator (Alice)'
      });
      setCurrentItem(res);
      await loadData();
      showToast('info', 'Loaded non-compliant sample post and executed review engine!');
    } catch (err: any) {
      showToast('error', err.message || 'Failed to load sample');
    }
  };

  // Pending queue items count
  const pendingCount = contentItems.filter(
    (i) => i.status === 'in_review' || i.status === 'changes_requested'
  ).length;

  return (
    <div className="min-h-screen bg-[#0a0f1d] text-slate-100 flex flex-col font-sans">
      {/* Top Navigation Bar */}
      <Navbar
        currentRole={userRole}
        onRoleChange={setUserRole}
        health={health}
        onResetDemo={handleResetDemo}
        isResetting={isResetting}
      />

      {/* Main Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          activeTab={activeTab}
          onTabChange={setActiveTab}
          pendingCount={pendingCount}
          brandName={activeBrand?.name || 'NovaTech'}
        />

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#0a0f1d]">
          <div className="max-w-7xl mx-auto">
            {activeTab === 'overview' && (
              <OverviewPage
                insights={insights}
                recentItems={contentItems}
                onNavigate={setActiveTab}
                onLoadSample={handleLoadSampleReview}
                isLoading={isLoading}
              />
            )}

            {activeTab === 'content_review' && (
              <ContentReviewPage
                brands={brands}
                activeBrand={activeBrand}
                onBrandSelect={handleBrandSelect}
                currentItem={currentItem}
                onItemUpdated={(item) => {
                  setCurrentItem(item);
                  loadData();
                }}
                onShowToast={showToast}
                userRole={userRole}
              />
            )}

            {activeTab === 'brand_guidelines' && (
              <BrandGuidelinesPage
                brand={activeBrand}
                onBrandUpdated={(b) => {
                  setActiveBrand(b);
                  loadData();
                }}
                onShowToast={showToast}
              />
            )}

            {activeTab === 'approved_facts' && (
              <ApprovedFactsPage
                facts={facts}
                activeBrand={activeBrand}
                onFactsUpdated={loadData}
                onShowToast={showToast}
              />
            )}

            {activeTab === 'review_queue' && (
              <ReviewQueuePage
                queueItems={contentItems.filter(
                  (i) => i.status === 'in_review' || i.status === 'changes_requested'
                )}
                userRole={userRole}
                onItemUpdated={loadData}
                onShowToast={showToast}
                onSelectRole={setUserRole}
              />
            )}

            {activeTab === 'review_history' && (
              <ReviewHistoryPage
                items={contentItems}
                onSelectReview={(item) => {
                  setCurrentItem(item);
                  setActiveTab('content_review');
                }}
              />
            )}

            {activeTab === 'governance_insights' && (
              <GovernanceInsightsPage insights={insights} />
            )}

            {activeTab === 'settings' && (
              <SettingsPage
                health={health}
                onResetDemo={handleResetDemo}
                isResetting={isResetting}
                onShowToast={showToast}
              />
            )}
          </div>
        </main>
      </div>

      {/* Floating Toast Alerts */}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}

export default App;
