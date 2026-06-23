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

export const analyticsApi = {
  dashboard: async () => (await api.get<DashboardAnalytics>('/analytics/dashboard')).data,
  trends: async (days = 30) => (await api.get<{ trends: { date: string; count: number }[] }>(`/analytics/trends?days=${days}`)).data,
  topBooks: async (limit = 5) => (await api.get<{ books: { book_id: string; title: string; author: string; borrow_count: number }[] }>(`/analytics/books?limit=${limit}`)).data,
};
