import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore, getRoleDashboardPath } from '../stores/authStore';
import type { UserRole } from '../stores/authStore';

interface ProtectedRouteProps {
  allowedRoles?: UserRole[];
  redirectTo?: string;
}

export function ProtectedRoute({
  allowedRoles,
  redirectTo = '/auth/login',
}: ProtectedRouteProps) {
  const { isAuthenticated, user } = useAuthStore();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
}

export function PublicOnlyRoute() {
  const { isAuthenticated, user } = useAuthStore();

  if (isAuthenticated && user) {
    return <Navigate to={getRoleDashboardPath(user.role)} replace />;
  }

  return <Outlet />;
}
