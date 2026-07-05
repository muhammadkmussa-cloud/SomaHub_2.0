import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  BookOpen,
  Users,
  BookMarked,
  BarChart2,
  Settings,
  LogOut,
  Library,
  ShoppingBag,
  Shield,
  Building2,
  ChevronLeft,
  ChevronRight,
  Home,
} from 'lucide-react';
import { cn } from '../ui';
import { useAuthStore, getRoleLabel } from '../../stores/authStore';
import type { UserRole } from '../../stores/authStore';
import api from '../../lib/api';

interface NavItem {
  label: string;
  to: string;
  icon: React.ReactNode;
  roles: UserRole[];
}

const navItems: NavItem[] = [
  { label: 'Overview',    to: '/dashboard',             icon: <Home size={18} />,       roles: ['super_admin', 'library_admin', 'librarian', 'reader'] },
  { label: 'Books',       to: '/dashboard/books',       icon: <BookOpen size={18} />,   roles: ['library_admin', 'librarian'] },
  { label: 'Borrowers',   to: '/dashboard/borrowers',   icon: <Users size={18} />,      roles: ['library_admin', 'librarian'] },
  { label: 'Loans',       to: '/dashboard/loans',       icon: <BookMarked size={18} />, roles: ['library_admin', 'librarian'] },
  { label: 'Fines',       to: '/dashboard/fines',       icon: <Library size={18} />,    roles: ['library_admin', 'librarian'] },
  { label: 'Bookstore',   to: '/dashboard/bookstore',   icon: <ShoppingBag size={18} />,roles: ['reader', 'super_admin'] },
  { label: 'My Library',  to: '/dashboard/my-library',  icon: <Library size={18} />,     roles: ['reader'] },
  { label: 'Analytics',   to: '/dashboard/analytics',   icon: <BarChart2 size={18} />,  roles: ['library_admin', 'super_admin'] },
  { label: 'Tenants',     to: '/dashboard/tenants',     icon: <Building2 size={18} />,  roles: ['super_admin'] },
  { label: 'Admin',       to: '/dashboard/admin',       icon: <Shield size={18} />,     roles: ['super_admin'] },
  { label: 'Settings',    to: '/dashboard/settings',    icon: <Settings size={18} />,   roles: ['library_admin', 'super_admin'] },
];

export function Sidebar() {
  const { user, clearAuth } = useAuthStore();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const visibleItems = navItems.filter(
    (item) => user && item.roles.includes(user.role),
  );

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout');
    } finally {
      clearAuth();
      navigate('/auth/login');
    }
  };

  return (
    <aside
      className={cn(
        'flex flex-col h-screen bg-obsidian-900 border-r border-obsidian-800 transition-all duration-300 select-none',
        collapsed ? 'w-16' : 'w-64',
      )}
    >
      {/* Logo */}
      <div className={cn('flex items-center gap-3 px-4 h-16 border-b border-obsidian-800', collapsed && 'justify-center px-2')}>
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center">
          <BookOpen size={16} className="text-white" />
        </div>
        {!collapsed && (
          <span className="font-display font-bold text-white text-lg tracking-tight">
            Soma<span className="text-emerald-400">Hub</span>
          </span>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-0.5">
        {visibleItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/dashboard'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150',
                isActive
                  ? 'bg-emerald-600 text-white'
                  : 'text-obsidian-400 hover:text-white hover:bg-obsidian-800',
                collapsed && 'justify-center px-2',
              )
            }
            title={collapsed ? item.label : undefined}
          >
            {item.icon}
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* User section */}
      <div className="border-t border-obsidian-800 p-3 space-y-1">
        {!collapsed && user && (
          <div className="px-2 py-2 mb-1">
            <p className="text-xs font-medium text-white truncate">
              {getRoleLabel(user.role)}
            </p>
            <p className="text-xs text-obsidian-500 truncate">{user.userId.slice(0, 8)}…</p>
          </div>
        )}
        <button
          onClick={handleLogout}
          className={cn(
            'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-obsidian-400 hover:text-red-400 hover:bg-obsidian-800 transition-all duration-150',
            collapsed && 'justify-center px-2',
          )}
          title={collapsed ? 'Logout' : undefined}
        >
          <LogOut size={18} />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed((c) => !c)}
        className="absolute -right-3 top-20 w-6 h-6 rounded-full bg-obsidian-700 border border-obsidian-600 text-obsidian-300 hover:text-white flex items-center justify-center transition-colors duration-150 z-10"
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
      </button>
    </aside>
  );
}
