import api from './api';

export interface Ebook {
  id: string;
  title: string;
  author: string;
  description?: string;
  category?: string;
  price: number;
  status: string;
  cover_url?: string;
  file_url?: string;
  content?: string;
}

// Resolves relative upload paths (/uploads/...) to absolute backend URLs
const BACKEND_BASE = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1').replace(
  /\/api\/v1\/?$/,
  '',
);
export function resolveUploadUrl(url: string | undefined | null): string | null {
  if (!url) return null;
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  return `${BACKEND_BASE}${url.startsWith('/') ? '' : '/'}${url}`;
}


export const ebooksApi = {
  list: async () => (await api.get<Ebook[]>('/ebooks')).data,
  get: async (id: string) => (await api.get<Ebook>(`/ebooks/${id}`)).data,
  myLibrary: async () => (await api.get('/ebook-purchases/my-library')).data,
  checkoutFree: async (ebookId: string) =>
    (await api.post(`/ebook-purchases/checkout-free?ebook_id=${ebookId}`)).data,
  addFavorite: async (ebookId: string) =>
    (await api.post('/favorites', { ebook_id: ebookId })).data,
  listFavorites: async () => (await api.get('/favorites')).data,
  create: async (data: Omit<Ebook, 'id'>) => (await api.post<Ebook>('/ebooks', data)).data,
  update: async (id: string, data: Partial<Ebook>) => (await api.put<Ebook>(`/ebooks/${id}`, data)).data,
  delete: async (id: string) => (await api.delete(`/ebooks/${id}`)).data,
  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return (await api.post<{ url: string }>('/ebooks/upload-file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })).data;
  },
  uploadCover: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return (await api.post<{ url: string }>('/ebooks/upload-cover', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })).data;
  },
  getProgress: async (ebookId: string) =>
    (await api.get<{ progress_percent: number; last_page: number }>(`/reading-progress/${ebookId}`)).data,
  updateProgress: async (ebookId: string, progressPercent: number, lastPage: number) =>
    (await api.post('/reading-progress', {
      ebook_id: ebookId,
      progress_percent: progressPercent,
      last_page: lastPage,
    })).data,
};
