import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { tenantsApi } from '../../lib/tenants';
import { Badge, Button } from '../../components/ui';
import { EmptyState, ErrorState, LoadingState, PageHeader, Panel } from './phase2Helpers';

export default function TenantsPage() {
  const queryClient = useQueryClient();
  const tenantsQuery = useQuery({ queryKey: ['tenants'], queryFn: tenantsApi.list });

  const toggleActive = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      tenantsApi.update(id, { is_active }),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['tenants'] }),
  });

  if (tenantsQuery.isLoading) return <LoadingState />;
  if (tenantsQuery.isError) return <ErrorState message="Failed to load tenants." />;

  const tenants = tenantsQuery.data ?? [];

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <PageHeader title="Tenants" description="Manage all library institutions on the platform." />

      <Panel title="All tenants">
        {tenants.length === 0 ? (
          <EmptyState label="No tenants registered." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-obsidian-500 border-b border-obsidian-100">
                  <th className="py-2 pr-4">Name</th>
                  <th className="py-2 pr-4">Slug</th>
                  <th className="py-2 pr-4">Plan</th>
                  <th className="py-2 pr-4">Status</th>
                  <th className="py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {tenants.map((tenant) => (
                  <tr key={tenant.id} className="border-b border-obsidian-50">
                    <td className="py-3 pr-4 font-medium text-obsidian-800">{tenant.name}</td>
                    <td className="py-3 pr-4 text-obsidian-500">{tenant.slug}</td>
                    <td className="py-3 pr-4">{tenant.plan}</td>
                    <td className="py-3 pr-4">
                      <Badge variant={tenant.is_active ? 'emerald' : 'danger'}>
                        {tenant.is_active ? 'active' : 'suspended'}
                      </Badge>
                    </td>
                    <td className="py-3">
                      <Button
                        size="sm"
                        variant="secondary"
                        loading={toggleActive.isPending}
                        onClick={() =>
                          toggleActive.mutate({ id: tenant.id, is_active: !tenant.is_active })
                        }
                      >
                        {tenant.is_active ? 'Suspend' : 'Activate'}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>
    </div>
  );
}
