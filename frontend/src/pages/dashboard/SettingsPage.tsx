import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { librariesApi, usersApi } from '../../lib/libraries';
import { Button, EmptyState, ErrorState, LoadingState, PageHeader, Panel, TextField } from './phase2Helpers';

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const profileQuery = useQuery({ queryKey: ['library-profile'], queryFn: librariesApi.getProfile });
  const userQuery = useQuery({ queryKey: ['user-me'], queryFn: usersApi.me });

  const updateLibrary = useMutation({
    mutationFn: librariesApi.updateProfile,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['library-profile'] }),
  });
  const updateUser = useMutation({
    mutationFn: usersApi.updateMe,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['user-me'] }),
  });

  if (profileQuery.isLoading || userQuery.isLoading) return <LoadingState />;
  if (profileQuery.isError) return <ErrorState message="Failed to load library profile." />;

  const profile = profileQuery.data;
  const user = userQuery.data;

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      <PageHeader title="Settings" description="Manage your library profile and account." />

      <Panel title="Library Profile">
        <form
          className="space-y-3"
          onSubmit={(e) => {
            e.preventDefault();
            const form = e.currentTarget;
            updateLibrary.mutate({
              name: (form.elements.namedItem('name') as HTMLInputElement).value,
              description: (form.elements.namedItem('description') as HTMLInputElement).value,
              address: (form.elements.namedItem('address') as HTMLInputElement).value,
              website: (form.elements.namedItem('website') as HTMLInputElement).value,
            });
          }}
        >
          <TextField name="name" label="Library name" defaultValue={profile?.name ?? ''} required />
          <TextField name="description" label="Description" defaultValue={profile?.description ?? ''} />
          <TextField name="address" label="Address" defaultValue={profile?.address ?? ''} />
          <TextField name="website" label="Website" defaultValue={profile?.website ?? ''} />
          <Button type="submit" loading={updateLibrary.isPending}>Save library</Button>
        </form>
      </Panel>

      <Panel title="Your Account">
        {user ? (
          <form
            className="space-y-3"
            onSubmit={(e) => {
              e.preventDefault();
              const username = (e.currentTarget.elements.namedItem('username') as HTMLInputElement).value;
              updateUser.mutate({ username });
            }}
          >
            <TextField name="username" label="Username" defaultValue={user.username} required />
            <p className="text-sm text-obsidian-500">Email: {user.email}</p>
            <Button type="submit" loading={updateUser.isPending}>Save account</Button>
          </form>
        ) : (
          <EmptyState label="User profile unavailable." />
        )}
      </Panel>
    </div>
  );
}
