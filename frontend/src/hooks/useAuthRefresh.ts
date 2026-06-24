import { useEffect } from 'react';
import api from '../lib/api';
import { useAuthStore } from '../stores/authStore';

export function useAuthRefresh() {
  const setAccessToken = useAuthStore((state) => state.setAccessToken);
  const clearAuth = useAuthStore((state) => state.clearAuth);

  useEffect(() => {
    const refresh = async () => {
      try {
        const response = await api.post('/auth/refresh-cookie', {}, { withCredentials: true });
        const { access_token } = response.data;
        if (access_token) {
          setAccessToken(access_token);
        }
      } catch {
        clearAuth();
      }
    };

    refresh();
  }, [setAccessToken, clearAuth]);
}
