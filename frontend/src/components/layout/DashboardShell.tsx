import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Sidebar } from './Sidebar';
import { Bell, Search } from 'lucide-react';
import { useAuthStore, getRoleLabel } from '../../stores/authStore';
import { notificationsApi } from '../../lib/notifications';

export function DashboardShell() {
  const { user } = useAuthStore();
  const [showNotifications, setShowNotifications] = useState(false);
  const queryClient = useQueryClient();

  const notificationsQuery = useQuery({
    queryKey: ['notifications'],
    queryFn: notificationsApi.list,
    enabled: !!user,
  });

  const markRead = useMutation({
    mutationFn: notificationsApi.markRead,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  });

  const unread = (notificationsQuery.data ?? []).filter((n) => n.status !== 'read').length;

  return (
    <div className="flex h-screen overflow-hidden bg-obsidian-50">
      <div className="relative flex-shrink-0 hidden lg:flex">
        <Sidebar />
      </div>

      <div className="flex flex-col flex-1 overflow-hidden">
        <header className="flex-shrink-0 h-16 bg-white border-b border-obsidian-100 flex items-center justify-between px-6 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="relative hidden md:flex items-center">
              <Search size={16} className="absolute left-3 text-obsidian-400" />
              <input
                type="text"
                placeholder="Search..."
                className="pl-9 pr-4 py-2 text-sm bg-obsidian-50 border border-obsidian-200 rounded-lg w-64 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 transition-all"
              />
            </div>
          </div>

          <div className="flex items-center gap-3 relative">
            <button
              type="button"
              onClick={() => setShowNotifications((v) => !v)}
              className="relative w-9 h-9 rounded-lg flex items-center justify-center text-obsidian-500 hover:bg-obsidian-100 transition-colors"
              aria-label="Notifications"
            >
              <Bell size={18} />
              {unread > 0 && (
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-emerald-500 rounded-full" />
              )}
            </button>

            {showNotifications && (
              <div className="absolute right-0 top-12 z-20 w-80 bg-white border border-obsidian-200 rounded-xl shadow-lg p-3 max-h-96 overflow-y-auto">
                <p className="text-sm font-semibold text-obsidian-800 mb-2">Notifications</p>
                {(notificationsQuery.data ?? []).length === 0 ? (
                  <p className="text-xs text-obsidian-400 py-4 text-center">No notifications</p>
                ) : (
                  <ul className="space-y-2">
                    {(notificationsQuery.data ?? []).map((n) => (
                      <li key={n.id} className="text-sm border-b border-obsidian-50 pb-2">
                        <p className="font-medium text-obsidian-800">{n.title}</p>
                        <p className="text-obsidian-500 text-xs">{n.message}</p>
                        {n.status !== 'read' && (
                          <button
                            type="button"
                            className="text-xs text-emerald-600 mt-1"
                            onClick={() => markRead.mutate(n.id)}
                          >
                            Mark read
                          </button>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {user && (
              <div className="flex items-center gap-2 pl-3 border-l border-obsidian-200">
                <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center text-white text-sm font-semibold">
                  {user.userId.slice(0, 1).toUpperCase()}
                </div>
                <div className="hidden sm:block">
                  <p className="text-xs font-semibold text-obsidian-800 leading-none">
                    {getRoleLabel(user.role)}
                  </p>
                </div>
              </div>
            )}
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
