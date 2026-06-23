import api from './api';
import type { Ebook } from './ebooks';

export const readerApi = {
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

export type { Ebook };
