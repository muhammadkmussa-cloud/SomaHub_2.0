import React, { useState, useRef } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { 
  User, 
  Lock, 
  Settings, 
  Building2, 
  Globe, 
  Laptop, 
  Smartphone, 
  Camera, 
  Trash2, 
  KeyRound, 
  ShieldAlert, 
  Sun, 
  Moon, 
  Monitor,
  Check,
  Bell
} from 'lucide-react';
import { librariesApi, usersApi } from '../../lib/libraries';
import { 
  Button, 
  EmptyState, 
  ErrorState, 
  LoadingState, 
  PageHeader, 
  Panel, 
  TextField,
  SelectField
} from './phase2Helpers';
import { Alert, Card, cn } from '../../components/ui';

type TabType = 'profile' | 'library' | 'security' | 'preferences';

const COMMON_TIMEZONES = [
  { value: 'UTC', label: 'Coordinated Universal Time (UTC)' },
  { value: 'America/New_York', label: 'Eastern Time (US & Canada)' },
  { value: 'America/Chicago', label: 'Central Time (US & Canada)' },
  { value: 'America/Denver', label: 'Mountain Time (US & Canada)' },
  { value: 'America/Los_Angeles', label: 'Pacific Time (US & Canada)' },
  { value: 'Europe/London', label: 'London, GMT' },
  { value: 'Europe/Paris', label: 'Paris, CET' },
  { value: 'Asia/Kolkata', label: 'India Standard Time (IST)' },
  { value: 'Asia/Tokyo', label: 'Tokyo, JST' },
  { value: 'Australia/Sydney', label: 'Sydney, AEST' },
];

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [activeTab, setActiveTab] = useState<TabType>('profile');
  const [profileMessage, setProfileMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [passwordMessage, setPasswordMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [preferencesMessage, setPreferencesMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Controlled preferences state
  const [themeVal, setThemeVal] = useState<string>('system');
  const [timezoneVal, setTimezoneVal] = useState<string>('UTC');
  const [emailNotifs, setEmailNotifs] = useState<boolean>(true);
  const [securityAlerts, setSecurityAlerts] = useState<boolean>(true);
  const [systemNews, setSystemNews] = useState<boolean>(false);
  const [fontSizeVal, setFontSizeVal] = useState<string>('medium');
  const [fontStyleVal, setFontStyleVal] = useState<string>('serif');

  // Queries
  const userQuery = useQuery({ queryKey: ['user-me'], queryFn: usersApi.me });
  const user = userQuery.data;

  // Derived role constants
  const role = user?.role;
  const isReader = role === 'reader';
  const isSuperAdmin = role === 'super_admin';
  const isLibraryStaff = role === 'library_admin' || role === 'librarian';

  // Sync state with query data when loaded
  React.useEffect(() => {
    if (user) {
      setThemeVal(user.theme || 'system');
      setTimezoneVal(user.timezone || 'UTC');
      if (user.role === 'reader') {
        setFontSizeVal(user.notification_prefs?.reading_font_size || 'medium');
        setFontStyleVal(user.notification_prefs?.reading_font_style || 'serif');
      } else {
        setEmailNotifs(user.notification_prefs?.email_notifs ?? true);
        setSecurityAlerts(user.notification_prefs?.security_alerts ?? true);
        setSystemNews(user.notification_prefs?.system_news ?? false);
      }
    }
  }, [user]);

  const profileQuery = useQuery({ 
    queryKey: ['library-profile'], 
    queryFn: librariesApi.getProfile,
    enabled: !!user?.tenant_id
  });
  const libraryProfile = profileQuery.data;

  const sessionsQuery = useQuery({
    queryKey: ['user-sessions'],
    queryFn: usersApi.getSessions,
    enabled: activeTab === 'security'
  });

  // Mutations
  const updateLibrary = useMutation({
    mutationFn: librariesApi.updateProfile,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['library-profile'] });
      setProfileMessage({ type: 'success', text: 'Library profile updated successfully.' });
    },
    onError: () => {
      setProfileMessage({ type: 'error', text: 'Failed to update library profile.' });
    }
  });

  const updateUserProfile = useMutation({
    mutationFn: usersApi.updateMe,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['user-me'] });
      setProfileMessage({ type: 'success', text: 'Profile updated successfully.' });
    },
    onError: () => {
      setProfileMessage({ type: 'error', text: 'Failed to update profile.' });
    }
  });

  const uploadAvatarMutation = useMutation({
    mutationFn: usersApi.uploadAvatar,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['user-me'] });
      setProfileMessage({ type: 'success', text: 'Avatar uploaded successfully.' });
    },
    onError: () => {
      setProfileMessage({ type: 'error', text: 'Failed to upload avatar.' });
    }
  });

  const changePasswordMutation = useMutation({
    mutationFn: usersApi.changePassword,
    onSuccess: () => {
      setPasswordMessage({ type: 'success', text: 'Password changed successfully. All other devices have been logged out.' });
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || 'Failed to change password. Ensure your current password is correct.';
      setPasswordMessage({ type: 'error', text: msg });
    }
  });

  const updatePreferencesMutation = useMutation({
    mutationFn: usersApi.updatePreferences,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['user-me'] });
      setPreferencesMessage({ type: 'success', text: 'Preferences updated successfully.' });
    },
    onError: () => {
      setPreferencesMessage({ type: 'error', text: 'Failed to save preferences.' });
    }
  });

  const revokeSessionMutation = useMutation({
    mutationFn: usersApi.revokeSession,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['user-sessions'] });
    }
  });

  const revokeOtherSessionsMutation = useMutation({
    mutationFn: usersApi.revokeOtherSessions,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['user-sessions'] });
    }
  });

  if (userQuery.isLoading) return <LoadingState />;
  if (userQuery.isError) return <ErrorState message="Failed to load user profile." />;

  if (profileQuery.isLoading && profileQuery.fetchStatus !== 'idle') return <LoadingState />;
  if (profileQuery.isError) return <ErrorState message="Failed to load library profile." />;

  // Handlers
  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file);
      uploadAvatarMutation.mutate(formData);
    }
  };

  const handleProfileSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setProfileMessage(null);
    const formData = new FormData(e.currentTarget);
    const username = formData.get('username') as string;
    const display_name = formData.get('display_name') as string;
    updateUserProfile.mutate({ username, display_name });
  };

  const handleLibrarySubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setProfileMessage(null);
    const formData = new FormData(e.currentTarget);
    updateLibrary.mutate({
      name: formData.get('name') as string,
      description: formData.get('description') as string,
      address: formData.get('address') as string,
      website: formData.get('website') as string,
    });
  };

  const handlePasswordSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setPasswordMessage(null);
    const formData = new FormData(e.currentTarget);
    const current_password = formData.get('current_password') as string;
    const new_password = formData.get('new_password') as string;
    const confirm_password = formData.get('confirm_password') as string;

    if (new_password !== confirm_password) {
      setPasswordMessage({ type: 'error', text: 'New passwords do not match.' });
      return;
    }

    changePasswordMutation.mutate({ current_password, new_password });
    e.currentTarget.reset();
  };

  const handlePreferencesSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setPreferencesMessage(null);

    let payload: any = { theme: themeVal };

    if (isReader) {
      payload.notification_prefs = {
        reading_font_size: fontSizeVal,
        reading_font_style: fontStyleVal
      };
    } else if (isSuperAdmin) {
      payload.timezone = timezoneVal;
      payload.notification_prefs = {
        security_alerts: securityAlerts,
        system_news: systemNews
      };
    } else {
      // library_admin / librarian
      payload.timezone = timezoneVal;
      payload.notification_prefs = {
        email_notifs: emailNotifs,
        security_alerts: securityAlerts,
        system_news: systemNews
      };
    }

    updatePreferencesMutation.mutate(payload);
  };

  // Session detection helper
  const getDeviceIcon = (ua: string) => {
    const lowercaseUa = ua.toLowerCase();
    if (lowercaseUa.includes('mobi') || lowercaseUa.includes('android') || lowercaseUa.includes('iphone')) {
      return <Smartphone className="text-obsidian-400" size={20} />;
    }
    if (lowercaseUa.includes('macintosh') || lowercaseUa.includes('windows') || lowercaseUa.includes('linux')) {
      return <Laptop className="text-obsidian-400" size={20} />;
    }
    return <Globe className="text-obsidian-400" size={20} />;
  };

  const getBrowserDetails = (ua: string) => {
    const lowercaseUa = ua.toLowerCase();
    let browser = 'Unknown Browser';
    let os = 'Unknown OS';

    if (lowercaseUa.includes('chrome') || lowercaseUa.includes('chromium')) browser = 'Google Chrome';
    else if (lowercaseUa.includes('firefox')) browser = 'Mozilla Firefox';
    else if (lowercaseUa.includes('safari')) browser = 'Apple Safari';
    else if (lowercaseUa.includes('edge')) browser = 'Microsoft Edge';

    if (lowercaseUa.includes('windows')) os = 'Windows';
    else if (lowercaseUa.includes('macintosh') || lowercaseUa.includes('mac os')) os = 'macOS';
    else if (lowercaseUa.includes('linux')) os = 'Linux';
    else if (lowercaseUa.includes('iphone') || lowercaseUa.includes('ipad')) os = 'iOS';
    else if (lowercaseUa.includes('android')) os = 'Android';

    return `${browser} on ${os}`;
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in pb-12">
      <PageHeader 
        title="Settings" 
        description="Configure your personal profile, security preferences, and system behavior." 
      />

      {/* Modern Horizontal Navigation Tabs */}
      {(() => {
        const tabs = (() => {
          if (isReader) return [
            { id: 'profile' as TabType, label: 'Profile', icon: <User size={16} /> },
            { id: 'preferences' as TabType, label: 'Interface', icon: <Settings size={16} /> },
            { id: 'security' as TabType, label: 'Security', icon: <Lock size={16} /> },
          ];
          if (isSuperAdmin) return [
            { id: 'profile' as TabType, label: 'Profile', icon: <User size={16} /> },
            { id: 'security' as TabType, label: 'Security', icon: <Lock size={16} /> },
            { id: 'preferences' as TabType, label: 'Preferences', icon: <Settings size={16} /> },
          ];
          // library_admin / librarian
          return [
            { id: 'profile' as TabType, label: 'Profile', icon: <User size={16} /> },
            ...(user?.tenant_id ? [{ id: 'library' as TabType, label: 'Library Details', icon: <Building2 size={16} /> }] : []),
            { id: 'security' as TabType, label: 'Security', icon: <Lock size={16} /> },
            { id: 'preferences' as TabType, label: 'Preferences', icon: <Settings size={16} /> },
          ];
        })();

        return (
          <div className="border-b border-obsidian-100 flex gap-2 overflow-x-auto scrollbar-none pb-px">
            {tabs.map((t) => (
              <button
                key={t.id}
                onClick={() => {
                  setActiveTab(t.id);
                  setProfileMessage(null);
                  setPasswordMessage(null);
                  setPreferencesMessage(null);
                }}
                className={cn(
                  "flex items-center gap-2 py-3 px-4 text-sm font-medium border-b-2 transition-all duration-150 whitespace-nowrap",
                  activeTab === t.id
                    ? "border-emerald-600 text-emerald-600"
                    : "border-transparent text-obsidian-500 hover:text-obsidian-800 hover:border-obsidian-200"
                )}
              >
                {t.icon}
                {t.label}
              </button>
            ))}
          </div>
        );
      })()}

      {/* Pane Content */}
      <div className="space-y-6">
        {/* Profile Tab */}
        {activeTab === 'profile' && user && (
          <div className="space-y-6">
            {profileMessage && (
              <Alert variant={profileMessage.type} onDismiss={() => setProfileMessage(null)}>
                {profileMessage.text}
              </Alert>
            )}

            <Card className="flex flex-col md:flex-row gap-6 items-center md:items-start p-6">
              {/* Avatar Uploader Section */}
              <div className="flex flex-col items-center gap-3">
                <div 
                  onClick={handleAvatarClick} 
                  className="relative group w-24 h-24 rounded-full overflow-hidden border border-obsidian-200 bg-obsidian-50 flex items-center justify-center cursor-pointer shadow-sm hover:shadow-md transition-all duration-200"
                >
                  {user.avatar_url ? (
                    <img 
                      src={user.avatar_url} 
                      alt="Avatar" 
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <span className="text-3xl font-display font-semibold text-emerald-600">
                      {((user.display_name || user.username || 'U').slice(0, 1)).toUpperCase()}
                    </span>
                  )}
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity duration-150">
                    <Camera className="text-white" size={20} />
                  </div>
                </div>
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleAvatarChange} 
                  accept="image/*" 
                  className="hidden"
                />
                <Button 
                  size="sm" 
                  variant="outline" 
                  onClick={handleAvatarClick}
                  loading={uploadAvatarMutation.isPending}
                >
                  Change Photo
                </Button>
              </div>

              {/* Personal Info fields */}
              <div className="flex-1 w-full space-y-4">
                <h3 className="font-display font-semibold text-obsidian-800 text-lg border-b pb-2">Profile Information</h3>
                
                <form onSubmit={handleProfileSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <TextField 
                      name="username" 
                      label="Username" 
                      defaultValue={user.username} 
                      required 
                    />
                    <TextField 
                      name="display_name" 
                      label="Display Name" 
                      defaultValue={user.display_name ?? ''} 
                      placeholder="e.g. John Doe"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-obsidian-500 block mb-1">Email (Unchangeable)</label>
                      <input 
                        type="text" 
                        value={user.email} 
                        disabled 
                        className="w-full h-10 rounded-lg border border-obsidian-200 bg-obsidian-50 px-3.5 text-sm text-obsidian-500 cursor-not-allowed"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-obsidian-500 block mb-1">Role</label>
                      <input 
                        type="text" 
                        value={user.role === 'super_admin' ? 'Super Admin' : user.role === 'library_admin' ? 'Library Admin' : user.role === 'librarian' ? 'Librarian' : 'Reader'} 
                        disabled 
                        className="w-full h-10 rounded-lg border border-obsidian-200 bg-obsidian-50 px-3.5 text-sm text-obsidian-500 cursor-not-allowed"
                      />
                    </div>
                  </div>

                  <div className="flex justify-end pt-2">
                    <Button type="submit" loading={updateUserProfile.isPending}>
                      Save Changes
                    </Button>
                  </div>
                </form>
              </div>
            </Card>
          </div>
        )}

        {/* Library Tab */}
        {activeTab === 'library' && user?.tenant_id && (
          <div className="space-y-6">
            {profileMessage && (
              <Alert variant={profileMessage.type} onDismiss={() => setProfileMessage(null)}>
                {profileMessage.text}
              </Alert>
            )}

            <Panel title="Library Configuration">
              <form onSubmit={handleLibrarySubmit} className="space-y-4">
                <TextField 
                  name="name" 
                  label="Library Name" 
                  defaultValue={libraryProfile?.name ?? ''} 
                  required 
                />
                <TextField 
                  name="description" 
                  label="Description" 
                  defaultValue={libraryProfile?.description ?? ''} 
                />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <TextField 
                    name="address" 
                    label="Address" 
                    defaultValue={libraryProfile?.address ?? ''} 
                  />
                  <TextField 
                    name="website" 
                    label="Website" 
                    defaultValue={libraryProfile?.website ?? ''} 
                    type="url"
                  />
                </div>
                <div className="flex justify-end pt-2">
                  <Button type="submit" loading={updateLibrary.isPending}>
                    Save Library Config
                  </Button>
                </div>
              </form>
            </Panel>
          </div>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <div className="space-y-6">
            {passwordMessage && (
              <Alert variant={passwordMessage.type} onDismiss={() => setPasswordMessage(null)}>
                {passwordMessage.text}
              </Alert>
            )}

            {user?.role === 'reader' ? (
              <div className="max-w-md">
                <Panel title="Update Password">
                  <p className="text-xs text-obsidian-400 mb-4">
                    Keep your account secure by using a strong, unique password.
                  </p>
                  <form onSubmit={handlePasswordSubmit} className="space-y-4">
                    <TextField 
                      name="current_password" 
                      label="Current Password" 
                      type="password" 
                      required 
                      minLength={8}
                    />
                    <TextField 
                      name="new_password" 
                      label="New Password" 
                      type="password" 
                      required 
                      minLength={8}
                    />
                    <TextField 
                      name="confirm_password" 
                      label="Confirm New Password" 
                      type="password" 
                      required 
                      minLength={8}
                    />
                    <Button 
                      type="submit" 
                      className="w-full"
                      leftIcon={<KeyRound size={16} />}
                      loading={changePasswordMutation.isPending}
                    >
                      Update Password
                    </Button>
                  </form>
                </Panel>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Change Password Pane */}
                <div className="lg:col-span-1">
                  <Panel title="Update Password">
                    <form onSubmit={handlePasswordSubmit} className="space-y-4">
                      <TextField 
                        name="current_password" 
                        label="Current Password" 
                        type="password" 
                        required 
                        minLength={8}
                      />
                      <TextField 
                        name="new_password" 
                        label="New Password" 
                        type="password" 
                        required 
                        minLength={8}
                      />
                      <TextField 
                        name="confirm_password" 
                        label="Confirm New Password" 
                        type="password" 
                        required 
                        minLength={8}
                      />
                      <Button 
                        type="submit" 
                        className="w-full"
                        leftIcon={<KeyRound size={16} />}
                        loading={changePasswordMutation.isPending}
                      >
                        Update Password
                      </Button>
                    </form>
                  </Panel>
                </div>

                {/* Sessions Pane */}
                <div className="lg:col-span-2 space-y-4">
                  <Card>
                    <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3 mb-6">
                      <div>
                        <h3 className="font-display font-semibold text-obsidian-800">Active Login Sessions</h3>
                        <p className="text-xs text-obsidian-400 mt-1">Manage active devices logged into this account.</p>
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-red-600 hover:text-red-700 hover:border-red-400 flex-shrink-0 self-start sm:self-center"
                        onClick={() => revokeOtherSessionsMutation.mutate()}
                        loading={revokeOtherSessionsMutation.isPending}
                        leftIcon={<ShieldAlert size={14} />}
                      >
                        Logout Other Devices
                      </Button>
                    </div>

                    {sessionsQuery.isLoading ? (
                      <LoadingState />
                    ) : sessionsQuery.isError ? (
                      <ErrorState message="Failed to retrieve active sessions." />
                    ) : (sessionsQuery.data ?? []).length === 0 ? (
                      <EmptyState label="No active sessions detected." />
                    ) : (
                      <div className="divide-y divide-obsidian-100 max-h-[350px] overflow-y-auto pr-1">
                        {(sessionsQuery.data ?? []).map((session: any) => (
                          <div key={session.session_id} className="py-3 flex items-center justify-between gap-3 text-sm">
                            <div className="flex items-center gap-3 min-w-0">
                              <div className="w-10 h-10 rounded-lg bg-obsidian-50 flex items-center justify-center flex-shrink-0">
                                {getDeviceIcon(session.user_agent)}
                              </div>
                              <div className="min-w-0">
                                <div className="flex items-center gap-1.5">
                                  <span className="font-semibold text-obsidian-800 truncate">
                                    {getBrowserDetails(session.user_agent)}
                                  </span>
                                  {session.is_current && (
                                    <span className="text-[10px] bg-emerald-100 text-emerald-700 font-semibold px-2 py-0.5 rounded-full flex-shrink-0">
                                      Current Device
                                    </span>
                                  )}
                                </div>
                                <p className="text-xs text-obsidian-400 mt-0.5">
                                  IP: {session.ip} • Logged in: {new Date(session.created_at).toLocaleString()}
                                </p>
                              </div>
                            </div>

                            {!session.is_current && (
                              <button
                                type="button"
                                onClick={() => revokeSessionMutation.mutate(session.session_id)}
                                disabled={revokeSessionMutation.isPending}
                                className="text-obsidian-400 hover:text-red-600 p-2 hover:bg-obsidian-50 rounded-lg transition-colors flex-shrink-0"
                                title="Revoke session"
                              >
                                <Trash2 size={16} />
                              </button>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </Card>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Preferences Tab */}
        {activeTab === 'preferences' && user && (
          <div className="space-y-6">
            {preferencesMessage && (
              <Alert variant={preferencesMessage.type} onDismiss={() => setPreferencesMessage(null)}>
                {preferencesMessage.text}
              </Alert>
            )}

            <form onSubmit={handlePreferencesSubmit} className="space-y-6">
              {/* Theme Preferences */}
              <Card>
                <h3 className="font-display font-semibold text-obsidian-800 mb-2">Display Theme</h3>
                <p className="text-xs text-obsidian-400 mb-6">Choose how SomaHub looks on your device.</p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* System Theme Card */}
                  <label className="cursor-pointer relative">
                    <input 
                      type="radio" 
                      name="theme" 
                      value="system" 
                      checked={themeVal === 'system'} 
                      onChange={() => setThemeVal('system')}
                      className="peer sr-only" 
                    />
                    <div className="flex items-center gap-3 p-4 border border-obsidian-200 rounded-xl hover:bg-obsidian-50 peer-checked:border-emerald-600 peer-checked:bg-emerald-50/30 transition-all">
                      <div className="w-8 h-8 rounded-lg bg-obsidian-100 flex items-center justify-center text-obsidian-600">
                        <Monitor size={18} />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-obsidian-800">System preference</p>
                        <p className="text-[10px] text-obsidian-400">Match operating system</p>
                      </div>
                      <div className="w-4 h-4 rounded-full border border-obsidian-300 flex items-center justify-center peer-checked:bg-emerald-600 peer-checked:border-emerald-600">
                        <Check size={10} className="text-white hidden peer-checked:block" />
                      </div>
                    </div>
                  </label>

                  {/* Light Theme Card */}
                  <label className="cursor-pointer relative">
                    <input 
                      type="radio" 
                      name="theme" 
                      value="light" 
                      checked={themeVal === 'light'} 
                      onChange={() => setThemeVal('light')}
                      className="peer sr-only" 
                    />
                    <div className="flex items-center gap-3 p-4 border border-obsidian-200 rounded-xl hover:bg-obsidian-50 peer-checked:border-emerald-600 peer-checked:bg-emerald-50/30 transition-all">
                      <div className="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center text-amber-600">
                        <Sun size={18} />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-obsidian-800">Light theme</p>
                        <p className="text-[10px] text-obsidian-400">Clean, crisp appearance</p>
                      </div>
                      <div className="w-4 h-4 rounded-full border border-obsidian-300 flex items-center justify-center peer-checked:bg-emerald-600 peer-checked:border-emerald-600">
                        <Check size={10} className="text-white hidden peer-checked:block" />
                      </div>
                    </div>
                  </label>

                  {/* Dark Theme Card */}
                  <label className="cursor-pointer relative">
                    <input 
                      type="radio" 
                      name="theme" 
                      value="dark" 
                      checked={themeVal === 'dark'} 
                      onChange={() => setThemeVal('dark')}
                      className="peer sr-only" 
                    />
                    <div className="flex items-center gap-3 p-4 border border-obsidian-200 rounded-xl hover:bg-obsidian-50 peer-checked:border-emerald-600 peer-checked:bg-emerald-50/30 transition-all">
                      <div className="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
                        <Moon size={18} />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-obsidian-800">Dark theme</p>
                        <p className="text-[10px] text-obsidian-400">Easy on the eyes in low light</p>
                      </div>
                      <div className="w-4 h-4 rounded-full border border-obsidian-300 flex items-center justify-center peer-checked:bg-emerald-600 peer-checked:border-emerald-600">
                        <Check size={10} className="text-white hidden peer-checked:block" />
                      </div>
                    </div>
                  </label>
                </div>
              </Card>

              {/* Reader Preferences Card */}
              {isReader && (
                <Card>
                  <h3 className="font-display font-semibold text-obsidian-800 mb-2">Reading Experience</h3>
                  <p className="text-xs text-obsidian-400 mb-6">Customize typography preferences for book reading.</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <SelectField
                      label="Font Size"
                      value={fontSizeVal}
                      onChange={(val) => setFontSizeVal(val)}
                    >
                      <option value="small">Small</option>
                      <option value="medium">Medium</option>
                      <option value="large">Large</option>
                    </SelectField>

                    <SelectField
                      label="Font Style"
                      value={fontStyleVal}
                      onChange={(val) => setFontStyleVal(val)}
                    >
                      <option value="serif">Serif (Classic Serif)</option>
                      <option value="sans-serif">Sans-serif (Modern Sans)</option>
                    </SelectField>
                  </div>
                </Card>
              )}

              {/* Super Admin Preferences */}
              {isSuperAdmin && (
                <>
                  {/* Timezone preferences */}
                  <Card>
                    <h3 className="font-display font-semibold text-obsidian-800 mb-2">Regional Preferences</h3>
                    <p className="text-xs text-obsidian-400 mb-6">Select your local timezone for correct timestamps.</p>
                    
                    <SelectField
                      label="Local Timezone"
                      value={timezoneVal}
                      onChange={(val) => setTimezoneVal(val)} 
                    >
                      {COMMON_TIMEZONES.map((tz) => (
                        <option key={tz.value} value={tz.value}>{tz.label}</option>
                      ))}
                    </SelectField>
                  </Card>

                  {/* Platform Notifications for Super Admin */}
                  <Card>
                    <div className="flex items-center gap-2 mb-2">
                      <Bell className="text-obsidian-600" size={18} />
                      <h3 className="font-display font-semibold text-obsidian-800">Platform Notifications</h3>
                    </div>
                    <p className="text-xs text-obsidian-400 mb-6">Configure platform alerts for your administrator account.</p>

                    <div className="space-y-4">
                      <label className="flex items-start gap-3 cursor-pointer group">
                        <input 
                          type="checkbox" 
                          name="security_alerts" 
                          checked={securityAlerts}
                          onChange={(e) => setSecurityAlerts(e.target.checked)}
                          className="w-4 h-4 mt-0.5 text-emerald-600 bg-white border-obsidian-200 rounded focus:ring-emerald-400 focus:outline-none"
                        />
                        <div>
                          <p className="text-sm font-semibold text-obsidian-800 group-hover:text-obsidian-900">Security alerts</p>
                          <p className="text-xs text-obsidian-400">Instant notification of new logins and password updates.</p>
                        </div>
                      </label>

                      <label className="flex items-start gap-3 cursor-pointer group">
                        <input 
                          type="checkbox" 
                          name="system_news" 
                          checked={systemNews}
                          onChange={(e) => setSystemNews(e.target.checked)}
                          className="w-4 h-4 mt-0.5 text-emerald-600 bg-white border-obsidian-200 rounded focus:ring-emerald-400 focus:outline-none"
                        />
                        <div>
                          <p className="text-sm font-semibold text-obsidian-800 group-hover:text-obsidian-900">System announcements</p>
                          <p className="text-xs text-obsidian-400">Get notified when new features and updates are deployed to the platform.</p>
                        </div>
                      </label>
                    </div>
                  </Card>
                </>
              )}

              {/* Library Staff Preferences */}
              {isLibraryStaff && (
                <>
                  {/* Timezone preferences */}
                  <Card>
                    <h3 className="font-display font-semibold text-obsidian-800 mb-2">Regional Preferences</h3>
                    <p className="text-xs text-obsidian-400 mb-6">Select your local timezone for correct timestamps.</p>
                    
                    <SelectField
                      label="Local Timezone"
                      value={timezoneVal}
                      onChange={(val) => setTimezoneVal(val)} 
                    >
                      {COMMON_TIMEZONES.map((tz) => (
                        <option key={tz.value} value={tz.value}>{tz.label}</option>
                      ))}
                    </SelectField>
                  </Card>

                  {/* Notification Preferences */}
                  <Card>
                    <div className="flex items-center gap-2 mb-2">
                      <Bell className="text-obsidian-600" size={18} />
                      <h3 className="font-display font-semibold text-obsidian-800">Notification Preferences</h3>
                    </div>
                    <p className="text-xs text-obsidian-400 mb-6">Configure how and when you receive automated updates.</p>

                    <div className="space-y-4">
                      <label className="flex items-start gap-3 cursor-pointer group">
                        <input 
                          type="checkbox" 
                          name="email_notifs" 
                          checked={emailNotifs}
                          onChange={(e) => setEmailNotifs(e.target.checked)}
                          className="w-4 h-4 mt-0.5 text-emerald-600 bg-white border-obsidian-200 rounded focus:ring-emerald-400 focus:outline-none"
                        />
                        <div>
                          <p className="text-sm font-semibold text-obsidian-800 group-hover:text-obsidian-900">Email notifications</p>
                          <p className="text-xs text-obsidian-400">Receive periodic status reports and borrow notifications.</p>
                        </div>
                      </label>

                      <label className="flex items-start gap-3 cursor-pointer group">
                        <input 
                          type="checkbox" 
                          name="security_alerts" 
                          checked={securityAlerts}
                          onChange={(e) => setSecurityAlerts(e.target.checked)}
                          className="w-4 h-4 mt-0.5 text-emerald-600 bg-white border-obsidian-200 rounded focus:ring-emerald-400 focus:outline-none"
                        />
                        <div>
                          <p className="text-sm font-semibold text-obsidian-800 group-hover:text-obsidian-900">Security alerts</p>
                          <p className="text-xs text-obsidian-400">Instant notification of new logins and password updates.</p>
                        </div>
                      </label>

                      <label className="flex items-start gap-3 cursor-pointer group">
                        <input 
                          type="checkbox" 
                          name="system_news" 
                          checked={systemNews}
                          onChange={(e) => setSystemNews(e.target.checked)}
                          className="w-4 h-4 mt-0.5 text-emerald-600 bg-white border-obsidian-200 rounded focus:ring-emerald-400 focus:outline-none"
                        />
                        <div>
                          <p className="text-sm font-semibold text-obsidian-800 group-hover:text-obsidian-900">System announcements</p>
                          <p className="text-xs text-obsidian-400">Get notified when new features and updates are deployed to the platform.</p>
                        </div>
                      </label>
                    </div>
                  </Card>
                </>
              )}

              <div className="flex justify-end">
                <Button type="submit" loading={updatePreferencesMutation.isPending}>
                  Save Preferences
                </Button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
