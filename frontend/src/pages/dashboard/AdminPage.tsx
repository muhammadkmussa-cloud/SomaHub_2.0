import { useQuery } from '@tanstack/react-query';
import api from '../../lib/api';
import { tenantsApi } from '../../lib/tenants';
import { Card } from '../../components/ui';
import { EmptyState, ErrorState, LoadingState, PageHeader } from './phase2Helpers';

export default function AdminPage() {
  const tenantsQuery = useQuery({ queryKey: ['tenants'], queryFn: tenantsApi.list });
  const usersQuery = useQuery({
    queryKey: ['admin-users'],
    queryFn: async () => (await api.get('/users')).data,
  });

  if (tenantsQuery.isLoading) return <LoadingState />;
  if (tenantsQuery.isError) return <ErrorState message="Failed to load admin data." />;

  const tenants = tenantsQuery.data ?? [];
  const users = usersQuery.data ?? [];
  const activeTenants = tenants.filter((t) => t.is_active).length;

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <PageHeader title="Super Admin" description="Platform-wide overview and management." />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Tenants', value: tenants.length },
          { label: 'Active Tenants', value: activeTenants },
          { label: 'Platform Users', value: users.length },
          { label: 'Suspended', value: tenants.length - activeTenants },
        ].map((item) => (
          <Card key={item.label}>
            <p className="text-2xl font-display font-bold text-obsidian-900">{item.value}</p>
            <p className="text-xs text-obsidian-500">{item.label}</p>
          </Card>
        ))}
      </div>

      <Card>
        <h2 className="font-display font-semibold text-obsidian-800 mb-4">Recent tenants</h2>
        {tenants.length === 0 ? (
          <EmptyState label="No tenants yet." />
        ) : (
          <ul className="space-y-2 text-sm text-obsidian-600">
            {tenants.slice(0, 8).map((t) => (
              <li key={t.id} className="flex justify-between">
                <span>{t.name}</span>
                <span className="text-obsidian-400">{t.plan}</span>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
