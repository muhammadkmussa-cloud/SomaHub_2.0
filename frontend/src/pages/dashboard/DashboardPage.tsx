import { useQuery } from '@tanstack/react-query';
import { useAuthStore, getRoleLabel } from '../../stores/authStore';
import { Card } from '../../components/ui';
import { analyticsApi } from '../../lib/analytics';
import {
  BookOpen,
  BookMarked,
  Users,
  AlertTriangle,
  ShoppingBag,
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
    queryFn: analyticsApi.dashboard,
    enabled: ['super_admin', 'library_admin', 'librarian'].includes(role),
  });

  const stats = analyticsQuery.data;

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
        <Card className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <ShoppingBag size={20} />
          </div>
          <div>
            <p className="font-medium text-obsidian-800">Visit the Bookstore</p>
            <p className="text-sm text-obsidian-500">Browse free and paid ebooks in your digital library.</p>
          </div>
        </Card>
      )}
    </div>
  );
}
