import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './lib/queryClient';
import { Spinner } from './components/ui';
import { ProtectedRoute } from './router/ProtectedRoute';
import { DashboardShell } from './components/layout/DashboardShell';
import { useAuthRefresh } from './hooks/useAuthRefresh';
import type { UserRole } from './stores/authStore';

const LandingPage         = lazy(() => import('./pages/LandingPage'));
const LoginPage           = lazy(() => import('./pages/auth/LoginPage'));
const SignupReaderPage    = lazy(() => import('./pages/auth/SignupReaderPage'));
const SignupLibraryPage   = lazy(() => import('./pages/auth/SignupLibraryPage'));
const ForgotPasswordPage  = lazy(() => import('./pages/auth/ForgotPasswordPage'));
const ResetPasswordPage   = lazy(() => import('./pages/auth/ResetPasswordPage'));
const VerifyEmailPage     = lazy(() => import('./pages/auth/VerifyEmailPage'));
const DashboardPage       = lazy(() => import('./pages/dashboard/DashboardPage'));
const BooksPage           = lazy(() => import('./pages/dashboard/BooksPage'));
const BorrowersPage       = lazy(() => import('./pages/dashboard/BorrowersPage'));
const LoansPage           = lazy(() => import('./pages/dashboard/LoansPage'));
const FinesPage           = lazy(() => import('./pages/dashboard/FinesPage'));
const SettingsPage        = lazy(() => import('./pages/dashboard/SettingsPage'));
const BookstorePage       = lazy(() => import('./pages/dashboard/BookstorePage'));
const MyLibraryPage       = lazy(() => import('./pages/dashboard/MyLibraryPage'));
const EbookDetailPage     = lazy(() => import('./pages/dashboard/EbookDetailPage'));
const AnalyticsPage       = lazy(() => import('./pages/dashboard/AnalyticsPage'));
const TenantsPage         = lazy(() => import('./pages/dashboard/TenantsPage'));
const AdminPage           = lazy(() => import('./pages/dashboard/AdminPage'));

const STAFF_ROLES: UserRole[] = ['library_admin', 'librarian'];
const ADMIN_ROLES: UserRole[] = ['library_admin', 'super_admin'];

function PageLoader() {
  return (
    <div className="min-h-screen bg-obsidian-950 flex items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <Spinner size="lg" className="text-emerald-500" />
        <p className="text-sm text-obsidian-400">Loading...</p>
      </div>
    </div>
  );
}

function NotFoundPage() {
  return (
    <div className="min-h-screen bg-obsidian-950 flex items-center justify-center text-center p-6">
      <div>
        <p className="text-8xl font-display font-bold text-emerald-600 mb-4">404</p>
        <h1 className="text-3xl font-display font-bold text-white mb-3">Page not found</h1>
        <p className="text-obsidian-400 mb-8">The page you're looking for doesn't exist.</p>
        <a href="/" className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-emerald-600 text-white font-medium hover:bg-emerald-700 transition-colors">
          Go home
        </a>
      </div>
    </div>
  );
}

function UnauthorizedPage() {
  return (
    <div className="min-h-screen bg-obsidian-950 flex items-center justify-center text-center p-6">
      <div>
        <p className="text-8xl font-display font-bold text-amber-500 mb-4">403</p>
        <h1 className="text-3xl font-display font-bold text-white mb-3">Access denied</h1>
        <p className="text-obsidian-400 mb-8">You don't have permission to access this page.</p>
        <a href="/dashboard" className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-emerald-600 text-white font-medium hover:bg-emerald-700 transition-colors">
          Go to dashboard
        </a>
      </div>
    </div>
  );
}

export default function App() {
  useAuthRefresh();

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/auth/login" element={<LoginPage />} />
            <Route path="/auth/signup/reader" element={<SignupReaderPage />} />
            <Route path="/auth/signup/library" element={<SignupLibraryPage />} />
            <Route path="/auth/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/auth/reset-password" element={<ResetPasswordPage />} />
            <Route path="/auth/verify-email" element={<VerifyEmailPage />} />

            <Route element={<ProtectedRoute />}>
              <Route element={<DashboardShell />}>
                <Route path="/dashboard" element={<DashboardPage />} />

                <Route element={<ProtectedRoute allowedRoles={STAFF_ROLES} />}>
                  <Route path="/dashboard/books" element={<BooksPage />} />
                  <Route path="/dashboard/borrowers" element={<BorrowersPage />} />
                  <Route path="/dashboard/loans" element={<LoansPage />} />
                  <Route path="/dashboard/fines" element={<FinesPage />} />
                </Route>

                <Route element={<ProtectedRoute allowedRoles={['reader', 'library_admin', 'super_admin']} />}>
                  <Route path="/dashboard/bookstore" element={<BookstorePage />} />
                  <Route path="/dashboard/my-library" element={<MyLibraryPage />} />
                  <Route path="/dashboard/bookstore/:ebookId" element={<EbookDetailPage />} />
                </Route>

                <Route element={<ProtectedRoute allowedRoles={ADMIN_ROLES} />}>
                  <Route path="/dashboard/analytics" element={<AnalyticsPage />} />
                  <Route path="/dashboard/settings" element={<SettingsPage />} />
                </Route>

                <Route element={<ProtectedRoute allowedRoles={['super_admin']} />}>
                  <Route path="/dashboard/tenants" element={<TenantsPage />} />
                  <Route path="/dashboard/admin" element={<AdminPage />} />
                </Route>
              </Route>
            </Route>

            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
