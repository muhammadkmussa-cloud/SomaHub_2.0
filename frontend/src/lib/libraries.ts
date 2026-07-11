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
  updateMe: async (data: { username?: string; display_name?: string }) => (await api.patch('/users/me', data)).data,
  uploadAvatar: async (formData: FormData) => 
    (await api.post('/users/me/avatar', formData, { headers: { 'Content-Type': 'multipart/form-data' } })).data,
  changePassword: async (data: any) => (await api.post('/users/me/change-password', data)).data,
  updatePreferences: async (data: any) => (await api.patch('/users/me/preferences', data)).data,
  getSessions: async () => (await api.get('/users/me/sessions')).data,
  revokeSession: async (sessionId: string) => (await api.delete(`/users/me/sessions/${sessionId}`)).data,
  revokeOtherSessions: async () => (await api.delete('/users/me/sessions')).data,
};
