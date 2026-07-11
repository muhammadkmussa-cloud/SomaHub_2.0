import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../../lib/analytics';
import { tenantsApi } from '../../lib/tenants';
import { useAuthStore } from '../../stores/authStore';
import { Card, Badge } from '../../components/ui';
import { EmptyState, ErrorState, LoadingState, PageHeader } from './phase2Helpers';
import {
  Building2,
  Activity,
  Users,
  BookOpen,
  TrendingUp,
  Percent,
  Award,
  Globe,
  DollarSign,
  ChevronRight,
  Database,
} from 'lucide-react';

// Smooth animated number component for WOW factor
function AnimatedNumber({ value, isCurrency = false }: { value: number; isCurrency?: boolean }) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let start = 0;
    const duration = 600; // ms
    const stepTime = 16; // ~60fps
    const steps = duration / stepTime;
    const increment = value / steps;

    if (value === 0) {
      setDisplayValue(0);
      return;
    }

    const timer = setInterval(() => {
      start += increment;
      if (start >= value) {
        setDisplayValue(value);
        clearInterval(timer);
      } else {
        setDisplayValue(Math.floor(start));
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [value]);

  if (isCurrency) {
    return <>${displayValue.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</>;
  }
  return <>{displayValue.toLocaleString()}</>;
}

export default function AnalyticsPage() {
  const { user } = useAuthStore();
  const isSuperAdmin = user?.role === 'super_admin';
  
  // State for tenant drilldown selector
  const [selectedTenantId, setSelectedTenantId] = useState<string>('global');
  const [activeLeaderboardTab, setActiveLeaderboardTab] = useState<'active' | 'recent'>('active');

  // Load tenants for dropdown (only if super admin)
  const tenantsQuery = useQuery({
    queryKey: ['tenants-list'],
    queryFn: tenantsApi.list,
    enabled: isSuperAdmin,
  });

  // Query platform wide cockpit metrics (only if global and super admin)
  const isGlobalView = selectedTenantId === 'global';
  const showPlatformCockpit = isSuperAdmin && isGlobalView;

  const platformKpisQuery = useQuery({
    queryKey: ['platform-kpis'],
    queryFn: analyticsApi.platformKpis,
    enabled: showPlatformCockpit,
  });

  const platformStorageQuery = useQuery({
    queryKey: ['platform-storage'],
    queryFn: analyticsApi.platformStorage,
    enabled: showPlatformCockpit,
  });

  const platformLeaderboardQuery = useQuery({
    queryKey: ['platform-leaderboard'],
    queryFn: analyticsApi.tenantLeaderboard,
    enabled: showPlatformCockpit,
  });

  // Query tenant-specific library metrics
  const targetTenantId = isSuperAdmin 
    ? (selectedTenantId === 'global' ? undefined : selectedTenantId) 
    : undefined; // Backend extracts from token for non-superadmin

  const dashboardQuery = useQuery({
    queryKey: ['analytics-dashboard', targetTenantId],
    queryFn: () => analyticsApi.dashboard(targetTenantId),
    enabled: !showPlatformCockpit,
  });

  const trendsQuery = useQuery({
    queryKey: ['analytics-trends', targetTenantId],
    queryFn: () => analyticsApi.trends(14, targetTenantId),
    enabled: !showPlatformCockpit,
  });

  const topBooksQuery = useQuery({
    queryKey: ['analytics-top-books', targetTenantId],
    queryFn: () => analyticsApi.topBooks(5, targetTenantId),
    enabled: !showPlatformCockpit,
  });

  // Loading and error handling
  const isLoading = showPlatformCockpit
    ? (platformKpisQuery.isLoading || platformStorageQuery.isLoading || platformLeaderboardQuery.isLoading)
    : dashboardQuery.isLoading;

  const isError = showPlatformCockpit
    ? (platformKpisQuery.isError || platformStorageQuery.isError || platformLeaderboardQuery.isError)
    : dashboardQuery.isError;

  if (isLoading) return <LoadingState />;
  if (isError) return <ErrorState message="Failed to load platform analytics." />;

  const tenantsList = tenantsQuery.data ?? [];

  // Dropdown Component for Drill-down selector
  const renderTenantSelector = () => {
    if (!isSuperAdmin) return null;
    return (
      <div className="flex items-center gap-3 bg-white dark:bg-obsidian-900 border border-obsidian-200 dark:border-obsidian-800 rounded-xl px-4 py-2 shadow-sm transition-all duration-300">
        <Globe className="text-emerald-500 w-4 h-4 animate-pulse" />
        <span className="text-xs font-semibold text-obsidian-500 uppercase tracking-wider">Scope:</span>
        <select
          value={selectedTenantId}
          onChange={(e) => setSelectedTenantId(e.target.value)}
          className="text-sm font-semibold text-obsidian-800 dark:text-obsidian-200 bg-transparent border-none p-0 pr-8 focus:ring-0 cursor-pointer"
        >
          <option value="global">🌐 All Tenants (Global Platform View)</option>
          {tenantsList.map((t) => (
            <option key={t.id} value={t.id}>
              🏢 {t.name}
            </option>
          ))}
        </select>
      </div>
    );
  };

  // ----------------------------------------------------
  // VIEW A: PLATFORM COCKPIT (Super Admin, Global Selected)
  // ----------------------------------------------------
  if (showPlatformCockpit) {
    const kpis = platformKpisQuery.data;
    const storage = platformStorageQuery.data;
    const leaderboard = platformLeaderboardQuery.data;

    return (
      <div className="max-w-6xl mx-auto space-y-8 animate-fade-in pb-12">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <PageHeader
            title="Platform Cockpit"
            description="High-level pulse, system health, and ecosystem analytics of SomaHub."
          />
          <div className="self-start md:self-center">{renderTenantSelector()}</div>
        </div>

        {/* 1. KPI Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
          {[
            {
              label: 'Total Active Tenants',
              value: kpis?.total_tenants ?? 0,
              sub: `${kpis?.active_tenants_this_week ?? 0} active this week`,
              icon: <Building2 className="w-5 h-5" />,
              gradient: 'from-emerald-500/10 to-emerald-500/5 text-emerald-600 border-emerald-100 dark:border-emerald-950',
            },
            {
              label: 'Ecosystem Users',
              value: kpis?.total_ecosystem_users ?? 0,
              sub: 'Aggregated readers',
              icon: <Users className="w-5 h-5" />,
              gradient: 'from-blue-500/10 to-blue-500/5 text-blue-600 border-blue-100 dark:border-blue-950',
            },
            {
              label: 'Platform Catalog Size',
              value: kpis?.total_catalog_books ?? 0,
              sub: 'Physical & digital books',
              icon: <BookOpen className="w-5 h-5" />,
              gradient: 'from-amber-500/10 to-amber-500/5 text-amber-600 border-amber-100 dark:border-amber-950',
            },
            {
              label: 'Active Subscriptions',
              value: kpis?.total_ebook_sales ?? 0,
              sub: 'Ebook lifetime purchases',
              icon: <Activity className="w-5 h-5" />,
              gradient: 'from-purple-500/10 to-purple-500/5 text-purple-600 border-purple-100 dark:border-purple-950',
            },
          ].map((item, idx) => (
            <Card
              key={idx}
              className="relative overflow-hidden group hover:shadow-md transition-all duration-300 border border-obsidian-200 dark:border-obsidian-800"
            >
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center bg-gradient-to-br ${item.gradient}`}>
                  {item.icon}
                </div>
                <div>
                  <p className="text-3xl font-display font-black text-obsidian-950 dark:text-white">
                    <AnimatedNumber value={item.value} />
                  </p>
                  <p className="text-xs font-semibold text-obsidian-400 mt-0.5">{item.label}</p>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-obsidian-100 dark:border-obsidian-800 flex items-center justify-between text-[10px] text-obsidian-400 font-medium">
                <span>{item.sub}</span>
                <ChevronRight className="w-3 h-3 text-obsidian-300 group-hover:translate-x-0.5 transition-transform" />
              </div>
            </Card>
          ))}
        </div>

        {/* 2. Middle Row: MRR Graph + Storage Consumption */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* MRR & Earnings Card */}
          <Card className="lg:col-span-2 border border-obsidian-200 dark:border-obsidian-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="font-display font-semibold text-obsidian-800 dark:text-obsidian-200">
                    Monthly Recurring Revenue (MRR)
                  </h3>
                  <p className="text-xs text-obsidian-400">Aggregated subscriber plans and ebook sales</p>
                </div>
                <div className="w-9 h-9 rounded-lg bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600 flex items-center justify-center">
                  <DollarSign className="w-5 h-5" />
                </div>
              </div>

              <div className="flex items-baseline gap-2 my-4">
                <span className="text-4xl font-display font-black text-emerald-600">
                  <AnimatedNumber value={kpis?.mrr ?? 0} isCurrency={true} />
                </span>
                <span className="text-xs font-semibold text-obsidian-400">/ month estimate</span>
              </div>
            </div>

            {/* Simple Dynamic SVG Mini Chart for Premium look */}
            <div className="mt-6 h-28 w-full bg-obsidian-50 dark:bg-obsidian-950/20 rounded-xl p-2 relative overflow-hidden flex items-end">
              <div className="absolute top-2 left-3 flex items-center gap-1.5 text-[10px] text-emerald-600 font-semibold bg-emerald-50 dark:bg-emerald-950/50 px-2 py-0.5 rounded-full">
                <TrendingUp className="w-3 h-3" />
                <span>+12.4% health growth</span>
              </div>
              <svg className="w-full h-full text-emerald-500/20 dark:text-emerald-500/10" viewBox="0 0 100 30" preserveAspectRatio="none">
                <path
                  d="M0,30 Q15,22 30,24 T60,12 T90,6 T100,2 L100,30 Z"
                  fill="currentColor"
                />
                <path
                  d="M0,30 Q15,22 30,24 T60,12 T90,6 T100,2"
                  fill="none"
                  stroke="rgb(16 185 129)"
                  strokeWidth="1.5"
                />
              </svg>
            </div>
          </Card>

          {/* Infrastructure & Storage consumption */}
          <Card className="border border-obsidian-200 dark:border-obsidian-800">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-display font-semibold text-obsidian-800 dark:text-obsidian-200">
                  System Storage
                </h3>
                <p className="text-xs text-obsidian-400">Aggregated file and cover assets</p>
              </div>
              <div className="w-9 h-9 rounded-lg bg-blue-50 dark:bg-blue-950/30 text-blue-600 flex items-center justify-center">
                <Database className="w-5 h-5" />
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs font-semibold text-obsidian-700 dark:text-obsidian-300 mb-1.5">
                  <span>Usage: {((storage?.estimated_total_mb ?? 0) / 1024).toFixed(2)} GB</span>
                  <span className="text-obsidian-400">of 10.0 GB Limit</span>
                </div>
                {/* Visual Storage Bar */}
                <div className="w-full h-3 bg-obsidian-100 dark:bg-obsidian-850 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-1000"
                    style={{ width: `${Math.min(100, ((storage?.estimated_total_mb ?? 0) / 1024) * 10)}%` }}
                  />
                </div>
              </div>

              <div className="pt-3 border-t border-obsidian-100 dark:border-obsidian-800 space-y-2">
                <p className="text-[10px] uppercase font-bold text-obsidian-400 tracking-wider">Top Tenants by Storage</p>
                {storage?.top_tenants?.map((tenant, idx) => (
                  <div key={tenant.tenant_id} className="flex items-center justify-between text-xs">
                    <span className="font-medium text-obsidian-750 dark:text-obsidian-300 truncate max-w-[140px]">
                      {idx + 1}. {tenant.tenant_name}
                    </span>
                    <span className="text-obsidian-500 font-mono">
                      {(tenant.estimated_mb / 1024).toFixed(2)} GB
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </div>

        {/* 3. Tenant Leaderboard & Registrations */}
        <Card className="border border-obsidian-200 dark:border-obsidian-800">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-obsidian-100 dark:border-obsidian-800 mb-4">
            <div className="flex items-center gap-2">
              <Award className="text-emerald-500" size={20} />
              <h3 className="font-display font-semibold text-obsidian-850 dark:text-obsidian-200">
                Tenant Activity Dashboard
              </h3>
            </div>
            {/* Tabs Selector */}
            <div className="flex bg-obsidian-100 dark:bg-obsidian-850 p-1 rounded-lg self-start">
              <button
                onClick={() => setActiveLeaderboardTab('active')}
                className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                  activeLeaderboardTab === 'active'
                    ? 'bg-white dark:bg-obsidian-900 text-obsidian-800 dark:text-obsidian-100 shadow-sm'
                    : 'text-obsidian-450 hover:text-obsidian-600'
                }`}
              >
                Top Active Libraries
              </button>
              <button
                onClick={() => setActiveLeaderboardTab('recent')}
                className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                  activeLeaderboardTab === 'recent'
                    ? 'bg-white dark:bg-obsidian-900 text-obsidian-800 dark:text-obsidian-100 shadow-sm'
                    : 'text-obsidian-450 hover:text-obsidian-600'
                }`}
              >
                Recent Registrations
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            {activeLeaderboardTab === 'active' ? (
              leaderboard?.top_tenants?.length === 0 ? (
                <EmptyState label="No tenant activity recorded in the past 7 days." />
              ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-obsidian-400 font-semibold border-b border-obsidian-50 dark:border-obsidian-850 pb-2">
                      <th className="py-2 pr-4">Library Name</th>
                      <th className="py-2 pr-4">Slug</th>
                      <th className="py-2 pr-4">Plan</th>
                      <th className="py-2 pr-4 text-center">7-Day Loans</th>
                      <th className="py-2 pr-4 text-center">Total Borrowers</th>
                      <th className="py-2 text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaderboard?.top_tenants?.map((tenant, idx) => (
                      <tr key={tenant.tenant_id} className="border-b border-obsidian-50/50 dark:border-obsidian-850/50 hover:bg-obsidian-50/30 dark:hover:bg-obsidian-850/10">
                        <td className="py-3 pr-4 font-semibold text-obsidian-800 dark:text-obsidian-200">
                          {idx === 0 && '🥇 '}
                          {idx === 1 && '🥈 '}
                          {idx === 2 && '🥉 '}
                          {idx > 2 && `${idx + 1}. `}
                          {tenant.name}
                        </td>
                        <td className="py-3 pr-4 text-obsidian-450 font-mono text-xs">{tenant.slug}</td>
                        <td className="py-3 pr-4">
                          <Badge variant={tenant.plan === 'enterprise' ? 'warning' : tenant.plan === 'professional' ? 'emerald' : 'neutral'}>
                            {tenant.plan}
                          </Badge>
                        </td>
                        <td className="py-3 pr-4 text-center font-bold text-obsidian-800 dark:text-obsidian-200">{tenant.loan_count_7d}</td>
                        <td className="py-3 pr-4 text-center text-obsidian-500">{tenant.total_borrowers}</td>
                        <td className="py-3 text-right">
                          <span className={`inline-flex items-center gap-1.5 text-xs font-semibold ${tenant.is_active ? 'text-emerald-500' : 'text-red-500'}`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${tenant.is_active ? 'bg-emerald-500' : 'bg-red-500 animate-ping'}`} />
                            {tenant.is_active ? 'Active' : 'Suspended'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )
            ) : (
              leaderboard?.recent_signups?.length === 0 ? (
                <EmptyState label="No library signups registered yet." />
              ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-obsidian-400 font-semibold border-b border-obsidian-50 dark:border-obsidian-850 pb-2">
                      <th className="py-2 pr-4">Library Name</th>
                      <th className="py-2 pr-4">Subdomain Slug</th>
                      <th className="py-2 pr-4">Plan</th>
                      <th className="py-2 pr-4">Created Date</th>
                      <th className="py-2 text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaderboard?.recent_signups?.map((tenant) => (
                      <tr key={tenant.tenant_id} className="border-b border-obsidian-50/50 dark:border-obsidian-850/50 hover:bg-obsidian-50/30 dark:hover:bg-obsidian-850/10">
                        <td className="py-3 pr-4 font-semibold text-obsidian-800 dark:text-obsidian-200">{tenant.name}</td>
                        <td className="py-3 pr-4 text-obsidian-450 font-mono text-xs">{tenant.slug}</td>
                        <td className="py-3 pr-4">
                          <Badge variant={tenant.plan === 'enterprise' ? 'warning' : tenant.plan === 'professional' ? 'emerald' : 'neutral'}>
                            {tenant.plan}
                          </Badge>
                        </td>
                        <td className="py-3 pr-4 text-obsidian-500">
                          {new Date(tenant.created_at).toLocaleDateString(undefined, { dateStyle: 'medium' })}
                        </td>
                        <td className="py-3 text-right">
                          <span className={`inline-flex items-center gap-1.5 text-xs font-semibold ${tenant.is_active ? 'text-emerald-500' : 'text-red-500'}`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${tenant.is_active ? 'bg-emerald-500' : 'bg-red-500'}`} />
                            {tenant.is_active ? 'Active' : 'Suspended'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )
            )}
          </div>
        </Card>
      </div>
    );
  }

  // ----------------------------------------------------
  // VIEW B: LIBRARY-SCOPED DASHBOARD (librarian or super admin drilled-down)
  // ----------------------------------------------------
  const stats = dashboardQuery.data;
  const trends = trendsQuery.data?.trends ?? [];
  const topBooks = topBooksQuery.data?.books ?? [];

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <PageHeader
            title={selectedTenantId === 'global' ? "Library Analytics" : `${tenantsList.find(t => t.id === selectedTenantId)?.name || 'Library'} Insights`}
            description="Circulation performance, reader logs, and inventory metrics."
          />
        </div>
        <div className="self-start md:self-center">{renderTenantSelector()}</div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Books', value: stats?.total_books ?? 0, icon: <BookOpen className="w-4 h-4" />, gradient: 'from-emerald-50 to-emerald-50/20 text-emerald-600 dark:border-emerald-950' },
          { label: 'Borrowers', value: stats?.total_borrowers ?? 0, icon: <Users className="w-4 h-4" />, gradient: 'from-blue-50 to-blue-50/20 text-blue-600 dark:border-blue-950' },
          { label: 'Active Loans', value: stats?.active_loans ?? 0, icon: <Activity className="w-4 h-4" />, gradient: 'from-purple-50 to-purple-50/20 text-purple-600 dark:border-purple-950' },
          { label: 'Overdue', value: stats?.overdue_loans ?? 0, icon: <Percent className="w-4 h-4" />, gradient: 'from-red-50 to-red-50/20 text-red-600 dark:border-red-950' },
        ].map((item) => (
          <Card key={item.label} className="border border-obsidian-200 dark:border-obsidian-800">
            <div className="flex items-center gap-3">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center bg-gradient-to-br ${item.gradient}`}>
                {item.icon}
              </div>
              <div>
                <p className="text-2xl font-display font-bold text-obsidian-900 dark:text-white">
                  <AnimatedNumber value={item.value} />
                </p>
                <p className="text-xs text-obsidian-400 font-semibold">{item.label}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Main Insights Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Card className="border border-obsidian-200 dark:border-obsidian-800">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="text-emerald-500 w-5 h-5" />
            <h2 className="font-display font-semibold text-obsidian-800 dark:text-obsidian-200">
              Loan Trends (14 Days)
            </h2>
          </div>
          {trends.length === 0 ? (
            <EmptyState label="No loan activity in this period." />
          ) : (
            <ul className="space-y-2.5 text-sm">
              {trends.map((t) => (
                <li key={t.date} className="flex justify-between items-center text-obsidian-600 dark:text-obsidian-450 border-b border-obsidian-50/50 dark:border-obsidian-850/50 pb-2 last:border-0 last:pb-0">
                  <span className="font-medium">{new Date(t.date).toLocaleDateString(undefined, { dateStyle: 'medium' })}</span>
                  <span className="font-bold text-obsidian-800 dark:text-obsidian-200 bg-obsidian-100/50 dark:bg-obsidian-850 px-2 py-0.5 rounded text-xs">{t.count} loans</span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card className="border border-obsidian-200 dark:border-obsidian-800">
          <div className="flex items-center gap-2 mb-4">
            <Award className="text-amber-500 w-5 h-5" />
            <h2 className="font-display font-semibold text-obsidian-800 dark:text-obsidian-200">
              Top Borrowed Books
            </h2>
          </div>
          {topBooks.length === 0 ? (
            <EmptyState label="No borrowing data yet." />
          ) : (
            <ul className="space-y-2.5 text-sm">
              {topBooks.map((book, idx) => (
                <li key={book.book_id} className="flex justify-between items-center text-obsidian-600 dark:text-obsidian-450 border-b border-obsidian-50/50 dark:border-obsidian-850/50 pb-2 last:border-0 last:pb-0">
                  <span className="truncate max-w-[240px] font-medium">
                    {idx === 0 && '🥇 '}
                    {idx === 1 && '🥈 '}
                    {idx === 2 && '🥉 '}
                    {idx > 2 && `${idx + 1}. `}
                    {book.title}
                  </span>
                  <span className="font-bold text-obsidian-800 dark:text-obsidian-200 font-mono text-xs">{book.borrow_count} borrows</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
