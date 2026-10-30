import {
  Brand,
  ApprovedFact,
  ContentItem,
  GovernanceInsights,
  HealthStatus,
  Finding,
  User,
  VisualAnalysisResponse
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '';

function getAuthToken(): string | null {
  return localStorage.getItem('brandguard_token');
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const token = getAuthToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...((options?.headers as Record<string, string>) || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers: options?.body instanceof FormData ? (token ? { 'Authorization': `Bearer ${token}` } : undefined) : headers,
  });

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorDetail = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // Health
  getHealth: () => request<HealthStatus>('/health'),

  // Brands
  getBrands: () => request<Brand[]>('/api/brands'),
  getBrand: (brandId: string) => request<Brand>(`/api/brands/${brandId}`),
  updateBrand: (brandId: string, updates: Partial<Brand>) =>
    request<Brand>(`/api/brands/${brandId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    }),

  // Approved Facts
  getFacts: (brandId?: string) =>
    request<ApprovedFact[]>(brandId ? `/api/facts?brand_id=${brandId}` : '/api/facts'),
  createFact: (data: Partial<ApprovedFact>) =>
    request<ApprovedFact>('/api/facts', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateFact: (factId: string, updates: Partial<ApprovedFact>) =>
    request<ApprovedFact>(`/api/facts/${factId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    }),
  deleteFact: (factId: string) =>
    request<{ message: string; id: string }>(`/api/facts/${factId}`, {
      method: 'DELETE',
    }),

  // Reviews
  getReviews: (brandId?: string, status?: string) => {
    const params = new URLSearchParams();
    if (brandId) params.append('brand_id', brandId);
    if (status) params.append('status', status);
    const qs = params.toString();
    return request<ContentItem[]>(`/api/reviews${qs ? `?${qs}` : ''}`);
  },
  getReview: (reviewId: string) => request<ContentItem>(`/api/reviews/${reviewId}`),
  createAndReview: (data: {
    id?: string;
    brand_id: string;
    title: string;
    content_type: string;
    channel: string;
    raw_content: string;
    image_alt_text?: string;
    campaign_ref?: string;
    created_by?: string;
  }) =>
    request<ContentItem>('/api/reviews', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  submitReview: (reviewId: string, action: { actor_name: string; actor_role: string; comments?: string }) =>
    request<ContentItem>(`/api/reviews/${reviewId}/submit`, {
      method: 'POST',
      body: JSON.stringify(action),
    }),
  approveReview: (reviewId: string, action: { actor_name: string; actor_role: string; comments?: string }) =>
    request<ContentItem>(`/api/reviews/${reviewId}/approve`, {
      method: 'POST',
      body: JSON.stringify(action),
    }),
  rejectReview: (reviewId: string, action: { actor_name: string; actor_role: string; comments?: string }) =>
    request<ContentItem>(`/api/reviews/${reviewId}/reject`, {
      method: 'POST',
      body: JSON.stringify(action),
    }),
  requestChanges: (reviewId: string, action: { actor_name: string; actor_role: string; comments?: string }) =>
    request<ContentItem>(`/api/reviews/${reviewId}/request-changes`, {
      method: 'POST',
      body: JSON.stringify(action),
    }),
  reviseContent: (reviewId: string, data: {
    content_text: string;
    image_alt_text?: string;
    change_summary: string;
    actor_name: string;
    actor_role: string;
  }) =>
    request<ContentItem>(`/api/reviews/${reviewId}/revise`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Findings
  updateFinding: (findingId: string, action: 'apply' | 'dismiss' | 'manual_edit', dismissal_reason?: string) =>
    request<{ message: string; finding_id: string; status: string }>(`/api/reviews/findings/${findingId}`, {
      method: 'PATCH',
      body: JSON.stringify({ action, dismissal_reason }),
    }),

  // Upload Document
  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<{ filename: string; size_bytes: number; content_text: string }>('/api/reviews/upload', {
      method: 'POST',
      body: formData,
    });
  },

  // Visual Asset Analysis (Round 3)
  analyzeVisualAsset: async (file: File, brandId: string, altText?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('brand_id', brandId);
    if (altText) formData.append('alt_text', altText);
    return request<VisualAnalysisResponse>('/api/visual/analyze', {
      method: 'POST',
      body: formData,
    });
  },
  getVisualHistory: (brandId?: string) =>
    request<any[]>(brandId ? `/api/visual/history?brand_id=${brandId}` : '/api/visual/history'),

  // Auth & Multi-User Governance (Round 3)
  login: (username: string, password: string) =>
    request<{ access_token: string; token_type: string; user: User }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),
  getMe: () => request<User>('/api/auth/me'),
  getUsers: () => request<User[]>('/api/auth/users'),

  // Insights
  getInsights: (brandId?: string) =>
    request<GovernanceInsights>(brandId ? `/api/insights?brand_id=${brandId}` : '/api/insights'),

  // Reset Demo
  resetDemo: () =>
    request<{ message: string }>('/api/reset-demo', {
      method: 'POST',
    }),
};
