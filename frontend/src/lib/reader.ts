import api from './api';
import type { Ebook } from './ebooks';

export const readerApi = {
  getOverview: async () =>
    (await api.get('/reader/overview')).data as ReaderOverview,
  getProgress: async (ebookId: string) =>
    (await api.get(`/reading-progress/${ebookId}`)).data,
  saveProgress: async (ebookId: string, progress: number) =>
    (
      await api.post('/reading-progress', {
        ebook_id: ebookId,
        progress_percent: progress,
      })
    ).data,
  listBookmarks: async (ebookId: string) =>
    (await api.get(`/bookmarks/ebook/${ebookId}`)).data,
  addBookmark: async (ebookId: string, page: number) =>
    (await api.post('/bookmarks', { ebook_id: ebookId, page_number: page })).data,
  listReviews: async (ebookId: string) =>
    (await api.get(`/reviews/ebook/${ebookId}`)).data,
  addReview: async (ebookId: string, rating: number, comment: string) =>
    (await api.post('/reviews', { ebook_id: ebookId, rating, comment })).data,
  checkOwned: async (ebookId: string) =>
    (await api.get(`/ebook-purchases/check/${ebookId}`)).data as { owned: boolean },
};

export interface LastReadEbook {
  ebook_id: string;
  title: string;
  author: string;
  cover_url: string | null;
  progress_percent: number;
  last_page: number;
  last_opened_at: string;
}

export interface ReaderOverview {
  last_read: LastReadEbook | null;
  books_completed_this_year: number;
  reading_goal_this_year: number;
  reading_streak_days: number;
}

export type { Ebook };

