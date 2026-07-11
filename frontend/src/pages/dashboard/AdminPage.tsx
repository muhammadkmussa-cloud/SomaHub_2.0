import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../../lib/analytics';
import { Card, Badge, Button } from '../../components/ui';
import { EmptyState, ErrorState, LoadingState, PageHeader } from './phase2Helpers';
import {
  Building2,
  Users,
  BookOpen,
  DollarSign,
  HardDrive,
  Activity,
  ArrowUpRight,
  TrendingUp,
  Clock,
} from 'lucide-react';

type BadgeVariant = 'emerald' | 'sapphire' | 'warning' | 'danger' | 'neutral';

const getPlanVariant = (plan: string): BadgeVariant => {
  const p = plan.toLowerCase().trim();
  if (p === 'enterprise' || p === 'professional') return 'sapphire';
  if (p === 'premium') return 'emerald';
  if (p === 'free' || p === 'basic') return 'warning';
  return 'neutral';
};

export default function AdminPage() {
  const kpisQuery = useQuery({ queryKey: ['platform-kpis'], queryFn: analyticsApi.platformKpis });
  const storageQuery = useQuery({ queryKey: ['platform-storage'], queryFn: analyticsApi.platformStorage });
  const leaderboardQuery = useQuery({ queryKey: ['platform-leaderboard'], queryFn: analyticsApi.tenantLeaderboard });

  if (kpisQuery.isLoading || storageQuery.isLoading || leaderboardQuery.isLoading) {
    return <LoadingState />;
  }

  if (kpisQuery.isError || storageQuery.isError || leaderboardQuery.isError) {
    return <ErrorState message="Failed to load platform administration metrics." />;
  }

  const kpis = kpisQuery.data;
  const storage = storageQuery.data;
  const leaderboard = leaderboardQuery.data;

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <PageHeader
        title="Super Admin Cockpit"
        description="Platform-wide ecosystem telemetry, tenant operations, and SaaS health indicators."
      />

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            label: 'Monthly Recurring Revenue',
            value: `$${(kpis?.mrr ?? 0).toLocaleString()}`,
            icon: <DollarSign size={20} />,
            color: 'text-emerald-600',
            bg: 'bg-emerald-50',
          },
          {
            label: 'Active / Total Tenants',
            value: `${kpis?.active_tenants_this_week ?? 0} / ${kpis?.total_tenants ?? 0}`,
            icon: <Building2 size={20} />,
            color: 'text-sapphire-600',
            bg: 'bg-sapphire-50',
          },
          {
            label: 'Ecosystem Users',
            value: (kpis?.total_ecosystem_users ?? 0).toLocaleString(),
            icon: <Users size={20} />,
            color: 'text-violet-600',
            bg: 'bg-violet-50',
          },
          {
            label: 'Total Catalog Books',
            value: (kpis?.total_catalog_books ?? 0).toLocaleString(),
            icon: <BookOpen size={20} />,
            color: 'text-amber-600',
            bg: 'bg-amber-50',
          },
        ].map((item) => (
          <Card key={item.label} className="flex items-start gap-4">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${item.bg} ${item.color}`}>
              {item.icon}
            </div>
            <div>
              <p className="text-2xl font-display font-bold text-obsidian-900">{item.value}</p>
              <p className="text-xs text-obsidian-500 mt-0.5">{item.label}</p>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Columns (Span 2): Tenants Lists */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Tenant Performance Leaderboard */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="font-display font-semibold text-obsidian-950">Active Tenant Performance</h2>
                <p className="text-xs text-obsidian-500 mt-0.5">Top-performing tenant libraries sorted by circulation volume.</p>
              </div>
              <TrendingUp size={18} className="text-obsidian-400" />
            </div>

            {(!leaderboard?.top_tenants || leaderboard.top_tenants.length === 0) ? (
              <EmptyState label="No active tenant activity telemetry recorded." />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-obsidian-100 text-xs font-semibold text-obsidian-500 uppercase tracking-wider">
                      <th className="pb-3">Library Name</th>
                      <th className="pb-3">Plan</th>
                      <th className="pb-3 text-right">Borrowers</th>
                      <th className="pb-3 text-right">7D Loans</th>
                      <th className="pb-3 text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-obsidian-50">
                    {leaderboard.top_tenants.map((tenant) => (
                      <tr key={tenant.tenant_id} className="hover:bg-obsidian-50/50 transition-colors">
                        <td className="py-3 font-medium text-obsidian-900">
                          <div>
                            <p className="font-semibold text-obsidian-900">{tenant.name}</p>
                            <p className="text-xs text-obsidian-400">/{tenant.slug}</p>
                          </div>
                        </td>
                        <td className="py-3">
                          <Badge variant={getPlanVariant(tenant.plan)}>
                            {tenant.plan}
                          </Badge>
                        </td>
                        <td className="py-3 text-right font-medium text-obsidian-600">
                          {tenant.total_borrowers}
                        </td>
                        <td className="py-3 text-right font-semibold text-obsidian-900">
                          {tenant.loan_count_7d}
                        </td>
                        <td className="py-3 text-right">
                          <Badge variant={tenant.is_active ? 'emerald' : 'danger'}>
                            {tenant.is_active ? 'Active' : 'Suspended'}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>

          {/* Recent Signups */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="font-display font-semibold text-obsidian-950">Recent Tenant Registrations</h2>
                <p className="text-xs text-obsidian-500 mt-0.5">Newly registered library organizations across the platform.</p>
              </div>
              <Clock size={18} className="text-obsidian-400" />
            </div>

            {(!leaderboard?.recent_signups || leaderboard.recent_signups.length === 0) ? (
              <EmptyState label="No recent signups in the last 30 days." />
            ) : (
              <div className="divide-y divide-obsidian-50">
                {leaderboard.recent_signups.map((tenant) => (
                  <div key={tenant.tenant_id} className="py-3 flex items-center justify-between hover:bg-obsidian-50/50 transition-colors rounded-lg px-2 -mx-2">
                    <div>
                      <h4 className="font-semibold text-sm text-obsidian-900">{tenant.name}</h4>
                      <p className="text-xs text-obsidian-400">Registered {new Date(tenant.created_at).toLocaleDateString()}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant={getPlanVariant(tenant.plan)}>{tenant.plan}</Badge>
                      <span className="text-xs font-semibold text-obsidian-500">{tenant.total_borrowers} members</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        {/* Right Column: Platform Storage & Actions */}
        <div className="space-y-6">
          {/* Storage & Infrastructure */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-display font-semibold text-obsidian-950">Ecosystem Storage</h2>
              <HardDrive size={18} className="text-obsidian-400" />
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="p-3 bg-obsidian-50 rounded-xl border border-obsidian-100">
                <p className="text-xs text-obsidian-500">Total Uploads</p>
                <p className="text-xl font-bold text-obsidian-900 mt-1">{(storage?.total_uploads ?? 0).toLocaleString()}</p>
              </div>
              <div className="p-3 bg-obsidian-50 rounded-xl border border-obsidian-100">
                <p className="text-xs text-obsidian-500">Estimated Size</p>
                <p className="text-xl font-bold text-obsidian-900 mt-1">{storage?.estimated_total_mb ? `${storage.estimated_total_mb.toFixed(1)} MB` : '0 MB'}</p>
              </div>
            </div>

            <h3 className="text-xs font-semibold uppercase tracking-wider text-obsidian-400 mb-3">Top Uploads by Tenant</h3>
            {(!storage?.top_tenants || storage.top_tenants.length === 0) ? (
              <p className="text-sm text-obsidian-500 italic py-2">No storage telemetry reported.</p>
            ) : (
              <div className="space-y-3">
                {storage.top_tenants.map((tenant) => (
                  <div key={tenant.tenant_id} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs text-obsidian-600">
                      <span className="font-semibold truncate max-w-[150px]">{tenant.tenant_name}</span>
                      <span>{tenant.estimated_mb.toFixed(1)} MB ({tenant.upload_count} files)</span>
                    </div>
                    <div className="w-full h-1.5 bg-obsidian-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-sapphire-500 rounded-full transition-all duration-300"
                        style={{
                          width: `${Math.min(100, (tenant.estimated_mb / (storage.estimated_total_mb || 1)) * 100)}%`
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Quick Operations panel */}
          <Card className="space-y-4">
            <h2 className="font-display font-semibold text-obsidian-950">Administrative Shortcuts</h2>
            
            <div className="flex flex-col gap-2">
              <Button variant="secondary" className="w-full justify-between" onClick={() => window.location.href = '/dashboard/tenants'}>
                <span>Manage Tenants</span>
                <ArrowUpRight size={16} />
              </Button>
              <Button variant="secondary" className="w-full justify-between" onClick={() => window.location.href = '/dashboard/settings'}>
                <span>Ecosystem Settings</span>
                <ArrowUpRight size={16} />
              </Button>
              <div className="p-3 bg-emerald-50/50 border border-emerald-100 rounded-xl flex items-center gap-3 mt-2">
                <Activity className="text-emerald-600 animate-pulse flex-shrink-0" size={18} />
                <div>
                  <p className="text-xs font-semibold text-emerald-800">Ecosystem Status</p>
                  <p className="text-[10px] text-emerald-600">All systems operational, Postgres and Redis connected.</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
