import api from './api';

export interface DashboardAnalytics {
  total_books: number;
  total_borrowers: number;
  active_loans: number;
  overdue_loans: number;
  total_fines_collected: number;
  total_ebook_sales: number;
  revenue_this_month: number;
}

export interface PlatformKPIs {
  total_tenants: number;
  active_tenants_this_week: number;
  total_ecosystem_users: number;
  total_catalog_books: number;
  total_ebook_sales: number;
  mrr: number;
}

export interface TenantStorageStat {
  tenant_id: string;
  tenant_name: string;
  upload_count: number;
  estimated_mb: number;
}

export interface StorageStats {
  total_uploads: number;
  estimated_total_mb: number;
  top_tenants: TenantStorageStat[];
}

export interface TenantLeaderboardEntry {
  tenant_id: string;
  name: string;
  slug: string;
  plan: string;
  loan_count_7d: number;
  total_borrowers: number;
  is_active: boolean;
  created_at: string;
}

export interface TenantLeaderboardResponse {
  top_tenants: TenantLeaderboardEntry[];
  recent_signups: TenantLeaderboardEntry[];
}

export const analyticsApi = {
  dashboard: async (tenantId?: string) => (await api.get<DashboardAnalytics>(tenantId ? `/analytics/dashboard?tenant_id=${tenantId}` : '/analytics/dashboard')).data,
  trends: async (days = 30, tenantId?: string) => (await api.get<{ trends: { date: string; count: number }[] }>(tenantId ? `/analytics/trends?days=${days}&tenant_id=${tenantId}` : `/analytics/trends?days=${days}`)).data,
  topBooks: async (limit = 5, tenantId?: string) => (await api.get<{ books: { book_id: string; title: string; author: string; borrow_count: number }[] }>(tenantId ? `/analytics/books?limit=${limit}&tenant_id=${tenantId}` : `/analytics/books?limit=${limit}`)).data,
  platformKpis: async () => (await api.get<PlatformKPIs>('/analytics/platform/kpis')).data,
  platformStorage: async () => (await api.get<StorageStats>('/analytics/platform/storage')).data,
  tenantLeaderboard: async () => (await api.get<TenantLeaderboardResponse>('/analytics/platform/leaderboard')).data,
};
