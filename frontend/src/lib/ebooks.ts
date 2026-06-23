import api from './api';

export interface Ebook {
  id: string;
  title: string;
  author: string;
  description?: string;
  category?: string;
  price: number;
  status: string;
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
};
