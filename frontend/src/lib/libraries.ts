import api from './api';

export interface LibraryProfile {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  address?: string;
  phone?: string;
  website?: string;
}

export const librariesApi = {
  getProfile: async () => (await api.get<LibraryProfile>('/libraries/profile')).data,
  updateProfile: async (data: Partial<LibraryProfile>) =>
    (await api.put('/libraries/profile', data)).data,
};

export const usersApi = {
  me: async () => (await api.get('/auth/me')).data,
  updateMe: async (data: { username?: string }) => (await api.patch('/users/me', data)).data,
};
