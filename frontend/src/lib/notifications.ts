import api from './api';

export interface Notification {
  id: string;
  title: string;
  message: string;
  status: string;
  category: string;
  created_at: string;
}

export const notificationsApi = {
  list: async () => (await api.get<Notification[]>('/notifications')).data,
  markRead: async (id: string) => (await api.post(`/notifications/${id}/read`)).data,
};
