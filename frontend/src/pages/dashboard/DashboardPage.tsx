import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useAuthStore, getRoleLabel } from '../../stores/authStore';
import { Card, Button } from '../../components/ui';
import { analyticsApi } from '../../lib/analytics';
import { readerApi } from '../../lib/reader';
import { resolveUploadUrl } from '../../lib/ebooks';
import {
  BookOpen,
  BookMarked,
  Users,
  AlertTriangle,
  ShoppingBag,
  Flame,
  Trophy,
} from 'lucide-react';

const ROLE_WELCOME: Record<string, { greeting: string; description: string }> = {
  super_admin: {
    greeting: 'Platform Overview',
    description: 'Manage all tenants, marketplace, and platform analytics.',
  },
  library_admin: {
    greeting: 'Library Dashboard',
    description: 'Monitor books, borrowers, loans, fines, and library analytics.',
  },
  librarian: {
    greeting: 'Librarian Workspace',
    description: 'Catalog books, register borrowers, issue and return books.',
  },
  reader: {
    greeting: 'Reader Dashboard',
    description: 'Browse the bookstore, read your books, and track your progress.',
  },
};

export default function DashboardPage() {
  const { user } = useAuthStore();
  const role = user?.role ?? 'reader';
  const meta = ROLE_WELCOME[role] ?? ROLE_WELCOME.reader;
  const roleLabel = user ? getRoleLabel(user.role) : '';

  const analyticsQuery = useQuery({
    queryKey: ['analytics-dashboard'],
    queryFn: () => analyticsApi.dashboard(),
    enabled: ['super_admin', 'library_admin', 'librarian'].includes(role),
  });

  const readerQuery = useQuery({
    queryKey: ['reader-overview'],
    queryFn: () => readerApi.getOverview(),
    enabled: role === 'reader',
  });

  const stats = analyticsQuery.data;
  const readerData = readerQuery.data;
  const currentYear = new Date().getFullYear();

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <div>
        <p className="text-sm text-obsidian-400 font-medium mb-0.5">{roleLabel}</p>
        <h1 className="text-2xl font-display font-bold text-obsidian-900">{meta.greeting}</h1>
        <p className="text-obsidian-500 mt-1">{meta.description}</p>
      </div>

      {['super_admin', 'library_admin', 'librarian'].includes(role) && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'Total Books', value: stats?.total_books ?? '—', icon: <BookOpen size={20} />, color: 'text-emerald-600', bg: 'bg-emerald-50' },
            { label: 'Active Loans', value: stats?.active_loans ?? '—', icon: <BookMarked size={20} />, color: 'text-sapphire-600', bg: 'bg-sapphire-50' },
            { label: 'Borrowers', value: stats?.total_borrowers ?? '—', icon: <Users size={20} />, color: 'text-violet-600', bg: 'bg-violet-50' },
            { label: 'Overdue', value: stats?.overdue_loans ?? '—', icon: <AlertTriangle size={20} />, color: 'text-amber-600', bg: 'bg-amber-50' },
          ].map((stat) => (
            <Card key={stat.label} className="flex items-start gap-4">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${stat.bg} ${stat.color}`}>
                {stat.icon}
              </div>
              <div>
                <p className="text-2xl font-display font-bold text-obsidian-900">{stat.value}</p>
                <p className="text-xs text-obsidian-500 mt-0.5">{stat.label}</p>
              </div>
            </Card>
          ))}
        </div>
      )}

      {role === 'reader' && (
        <div className="space-y-6">
          {/* Continue Reading Card */}
          <Card className="overflow-hidden border border-obsidian-100">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-obsidian-400 mb-4">Active Reading</h2>
            {readerData?.last_read ? (
              <div className="flex flex-col sm:flex-row gap-5 items-center sm:items-stretch">
                <div className="w-24 h-32 rounded-lg overflow-hidden border border-obsidian-100 shrink-0 shadow-sm bg-obsidian-50">
                  {readerData.last_read.cover_url ? (
                    <img
                      src={resolveUploadUrl(readerData.last_read.cover_url) ?? ''}
                      alt={readerData.last_read.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-obsidian-300">
                      <BookOpen size={32} />
                    </div>
                  )}
                </div>
                <div className="flex-1 flex flex-col justify-between w-full">
                  <div>
                    <h3 className="font-display font-bold text-lg text-obsidian-900 leading-tight">
                      {readerData.last_read.title}
                    </h3>
                    <p className="text-sm text-obsidian-500 mt-1">{readerData.last_read.author}</p>
                  </div>
                  
                  <div className="mt-4 sm:mt-0 space-y-2">
                    <div className="flex items-center justify-between text-xs text-obsidian-500 font-medium">
                      <span>Progress</span>
                      <span>{readerData.last_read.progress_percent}% read</span>
                    </div>
                    <div className="w-full h-2 bg-obsidian-50 rounded-full overflow-hidden border border-obsidian-100">
                      <div
                        className="h-full bg-emerald-500 rounded-full transition-all duration-300"
                        style={{ width: `${readerData.last_read.progress_percent}%` }}
                      />
                    </div>
                  </div>
                </div>
                <div className="flex items-center shrink-0 w-full sm:w-auto">
                  <Link to={`/dashboard/my-library/read/${readerData.last_read.ebook_id}`} className="w-full">
                    <Button className="w-full">Resume Reading</Button>
                  </Link>
                </div>
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row items-center gap-4 py-3">
                <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
                  <ShoppingBag size={24} />
                </div>
                <div className="flex-1 text-center sm:text-left">
                  <p className="font-semibold text-obsidian-800">No books in progress yet</p>
                  <p className="text-sm text-obsidian-500 mt-0.5">Explore our selection and start your next reading adventure.</p>
                </div>
                <Link to="/dashboard/bookstore" className="shrink-0 w-full sm:w-auto">
                  <Button variant="secondary" className="w-full">Browse Bookstore</Button>
                </Link>
              </div>
            )}
          </Card>

          {/* Yearly Stats Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-sapphire-50 text-sapphire-600 flex items-center justify-center shrink-0">
                <Trophy size={22} />
              </div>
              <div>
                <p className="text-2xl font-display font-bold text-obsidian-900">
                  {readerData?.books_completed_this_year ?? 0} of {readerData?.reading_goal_this_year ?? 12}
                </p>
                <p className="text-sm font-semibold text-obsidian-800 mt-0.5">Books Completed</p>
                <p className="text-xs text-obsidian-500 mt-1">Goal progress in {currentYear}</p>
              </div>
            </Card>

            <Card className="flex items-start gap-4">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${
                (readerData?.reading_streak_days ?? 0) > 0 ? 'bg-amber-50 text-amber-600 shadow-sm shadow-amber-100/50' : 'bg-obsidian-50 text-obsidian-400'
              }`}>
                <Flame size={22} className={(readerData?.reading_streak_days ?? 0) > 0 ? 'animate-pulse' : ''} />
              </div>
              <div>
                <p className="text-2xl font-display font-bold text-obsidian-900">
                  {(readerData?.reading_streak_days ?? 0) === 0 ? '—' : `${readerData?.reading_streak_days}-day streak`}
                </p>
                <p className="text-sm font-semibold text-obsidian-800 mt-0.5">Reading Streak</p>
                <p className="text-xs text-obsidian-500 mt-1">
                  {(readerData?.reading_streak_days ?? 0) > 0 ? '🔥 Keep the fire burning!' : 'Read daily to build a habit'}
                </p>
              </div>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}

