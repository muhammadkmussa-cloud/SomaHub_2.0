import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type UserRole = 'super_admin' | 'library_admin' | 'librarian' | 'reader';

export interface AuthUser {
  userId: string;
  role: UserRole;
  tenantId?: string | null;
}

interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  isAuthenticated: boolean;

  // Actions
  setAuth: (user: AuthUser, accessToken: string) => void;
  setAccessToken: (token: string) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,

      setAuth: (user, accessToken) =>
        set({ user, accessToken, isAuthenticated: true }),

      setAccessToken: (accessToken) =>
        set({ accessToken }),

      clearAuth: () =>
        set({ user: null, accessToken: null, isAuthenticated: false }),
    }),
    {
      name: 'somahub-auth',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        // Note: accessToken is NOT persisted (re-fetched via cookie on reload)
      }),
    },
  ),
);

// ── Role helpers ──────────────────────────────────────────────────────────────
export const ROLE_HIERARCHY: UserRole[] = [
  'reader',
  'librarian',
  'library_admin',
  'super_admin',
];

export const hasMinimumRole = (userRole: UserRole, minRole: UserRole): boolean => {
  return ROLE_HIERARCHY.indexOf(userRole) >= ROLE_HIERARCHY.indexOf(minRole);
};

export const isLibraryStaff = (role: UserRole): boolean =>
  ['librarian', 'library_admin'].includes(role);

export const getRoleDashboardPath = (role: UserRole): string => {
  switch (role) {
    case 'super_admin':    return '/dashboard/admin';
    case 'library_admin':  return '/dashboard';
    case 'librarian':      return '/dashboard';
    case 'reader':         return '/dashboard/bookstore';
    default:               return '/dashboard';
  }
};

export const getRoleLabel = (role: UserRole): string => {
  const labels: Record<UserRole, string> = {
    super_admin: 'Super Admin',
    library_admin: 'Library Administrator',
    librarian: 'Librarian',
    reader: 'Reader',
  };
  return labels[role] ?? role;
};
