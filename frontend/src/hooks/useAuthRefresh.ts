import { useEffect } from 'react';
import axios from 'axios';
import { useAuthStore } from '../stores/authStore';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1';

export function useAuthRefresh() {
  const setAccessToken = useAuthStore((state) => state.setAccessToken);
  const clearAuth = useAuthStore((state) => state.clearAuth);

  useEffect(() => {
    const refresh = async () => {
      try {
        // Use plain axios (not the intercepted api) so the 401 interceptor
        // doesn't fire a secondary refresh attempt here and cause an infinite reload.
        const response = await axios.post(
          `${BASE_URL}/auth/refresh-cookie`,
          {},
          { withCredentials: true },
        );
        const { access_token } = response.data;
        if (access_token) {
          setAccessToken(access_token);
        } else {
          clearAuth();
        }
      } catch {
        // refresh-cookie returned 401 or failed — session is gone, clear state.
        // ProtectedRoute will redirect to /auth/login automatically.
        clearAuth();
      }
    };

    refresh();
  }, [setAccessToken, clearAuth]);
}

