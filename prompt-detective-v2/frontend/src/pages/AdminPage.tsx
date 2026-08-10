import React, { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  BadgeCheck,
  BarChart3,
  Crown,
  Loader2,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  Users,
  Zap,
  X,
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { adminService, AdminDashboardStats, UserDetail } from '../services/adminService';
import PageContainer from '../components/page/PageContainer';
import PageHeader from '../components/PageHeader';
import PageSection from '../components/page/PageSection';
import Card from '../components/ui/Card';
import Chip from '../components/ui/Chip';
import { Button } from '../components/ui/Button';

const AdminPage: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<AdminDashboardStats | null>(null);
  const [users, setUsers] = useState<UserDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUser, setSelectedUser] = useState<UserDetail | null>(null);
  const [showUserModal, setShowUserModal] = useState(false);

  const isAuthorized = Boolean(user && (user.is_admin || user.is_super_admin));

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [dashboardStats, allUsers] = await Promise.all([
        adminService.getDashboardStats(),
        adminService.getUsers({ limit: 100 })
      ]);
      setStats(dashboardStats);
      setUsers(allUsers);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load dashboard data');
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      await loadDashboardData();
      return;
    }
    try {
      setLoading(true);
      const results = await adminService.getUsers({ 
        search: searchQuery,
        limit: 100
      });
      setUsers(results);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleTogglePremium = async (userId: number) => {
    try {
      await adminService.togglePremium(userId);
      await loadDashboardData();
    } catch (err: any) {
      alert('Failed to toggle premium: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleResetUsage = async (userId: number) => {
    if (confirm('Reset this user\'s API usage?')) {
      try {
        await adminService.resetUserUsage(userId);
        await loadDashboardData();
      } catch (err: any) {
        alert('Failed to reset usage: ' + (err.response?.data?.detail || err.message));
      }
    }
  };

  const handleViewUser = async (userId: number) => {
    try {
      const userDetails = await adminService.getUserDetails(userId);
      setSelectedUser(userDetails);
      setShowUserModal(true);
    } catch (err: any) {
      alert('Failed to load user details: ' + (err.response?.data?.detail || err.message));
    }
  };

  const statCards = useMemo(
    () => [
      {
        key: 'total_users',
        label: 'Total users',
        value: stats?.total_users ?? 0,
        helper: `${stats?.active_users ?? 0} active • ${stats?.verified_users ?? 0} verified`,
        icon: <Users className="h-5 w-5 text-blue-500" />,
      },
      {
        key: 'premium_users',
        label: 'Premium accounts',
        value: stats?.premium_users ?? 0,
        helper:
          stats && stats.total_users
            ? `${Math.round((stats.premium_users / stats.total_users) * 100)}% of user base`
            : '—',
        icon: <Crown className="h-5 w-5 text-amber-500" />,
      },
      {
        key: 'analyses',
        label: 'Total analyses',
        value: stats?.total_analyses ?? 0,
        helper: `${stats?.analyses_today ?? 0} processed today`,
        icon: <BarChart3 className="h-5 w-5 text-purple-500" />,
      },
      {
        key: 'api_calls',
        label: 'API calls',
        value: stats?.total_api_calls ?? 0,
        helper: 'Platform-wide requests',
        icon: <Activity className="h-5 w-5 text-emerald-500" />,
      },
    ],
    [stats]
  );

  const membershipDistribution = useMemo(
    () => [
      {
        label: 'Free tier',
        value: stats?.subscription_breakdown.free ?? 0,
        tone: 'gray',
      },
      {
        label: 'Pro tier',
        value: stats?.subscription_breakdown.pro ?? 0,
        tone: 'blue',
      },
      {
        label: 'Business / Enterprise',
        value: stats?.subscription_breakdown.enterprise ?? 0,
        tone: 'purple',
      },
    ],
    [stats]
  );

  if (!isAuthorized) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <Card variant="elevated" padding="lg" className="text-center">
          <div className="flex flex-col items-center gap-4">
            <ShieldCheck className="h-12 w-12 text-blue-500" />
            <h2 className="text-2xl font-semibold text-gray-900">Restricted area</h2>
            <p className="text-sm text-gray-600">You need admin permissions to access this dashboard.</p>
          </div>
        </Card>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatUsageLimit = (limit: number) => {
    return limit === -1 ? 'Unlimited' : limit.toLocaleString();
  };

  return (
    <PageContainer>
      <PageHeader
        title="Admin control center"
        subtitle="Monitor adoption, manage user access, and keep the reverse engineering pipeline healthy."
        breadcrumbs={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'Admin' }]}
        primaryAction={{ label: 'Refresh data', onClick: loadDashboardData }}
        secondaryAction={{ label: 'Export snapshot', onClick: () => console.log('Exporting dashboard snapshot') }}
        illustration={<Sparkles className="h-10 w-10 text-indigo-500" />}
      />

      <div className="flex flex-wrap gap-3 text-sm text-slate-500 dark:text-slate-400">
        <Chip tone="blue" size="sm">Live analytics</Chip>
        <Chip tone="emerald" size="sm">User orchestration</Chip>
        <Chip tone="purple" size="sm">Pipeline monitoring</Chip>
      </div>

      {error && (
        <Card variant="outline" padding="md" className="mt-6 border-red-200/60 bg-red-50/50 text-red-700 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-200">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <BadgeCheck className="h-5 w-5" />
              <div>
                <p className="text-sm font-semibold">We hit a snag while loading analytics.</p>
                <p className="text-xs opacity-80">{error}</p>
              </div>
            </div>
            <Button size="sm" variant="ghost" leadingIcon={<RefreshCw className="h-4 w-4" />} onClick={loadDashboardData}>
              Retry
            </Button>
          </div>
        </Card>
      )}

      <PageSection
        title="Realtime snapshot"
        description="Key health indicators for Prompt Detective across users and workloads."
        icon={<Activity className="h-6 w-6" />}
        variant="translucent"
      >
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {statCards.map((card) => (
            <Card
              key={card.key}
              variant="outline"
              padding="lg"
              className="flex flex-col gap-4 bg-white/80 dark:bg-slate-900/70"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-500 dark:text-slate-300">{card.label}</p>
                  <p className="mt-2 text-3xl font-semibold text-slate-900 dark:text-white">
                    {card.value.toLocaleString()}
                  </p>
                </div>
                <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-500 dark:bg-indigo-500/10 dark:text-indigo-200">
                  {card.icon}
                </span>
              </div>
              <p className="text-xs uppercase tracking-wide text-slate-400 dark:text-slate-500">{card.helper}</p>
            </Card>
          ))}
        </div>
      </PageSection>

      <PageSection
        title="Membership mix"
        description="How creators, power users, and teams are distributed across plans."
        icon={<Users className="h-6 w-6" />}
      >
        <div className="grid gap-4 md:grid-cols-3">
          {membershipDistribution.map((tier) => {
            const totalUsers = stats?.total_users ?? 1;
            const percentage = totalUsers ? Math.round((tier.value / totalUsers) * 100) : 0;

            return (
              <Card key={tier.label} variant="outline" padding="lg" className="bg-white/80 dark:bg-slate-900/70">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">{tier.label}</p>
                <p className="mt-3 text-3xl font-semibold text-slate-900 dark:text-white">{tier.value.toLocaleString()}</p>
                <div className="mt-4 flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                  <span className="flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-600 dark:border-slate-700 dark:bg-slate-900">
                    <Sparkles className="h-4 w-4" />
                  </span>
                  <span>{percentage}% of the user base</span>
                </div>
                <div className="mt-4 h-2 w-full rounded-full bg-slate-200 dark:bg-slate-800">
                  <div
                    className={`h-2 rounded-full ${
                      tier.tone === 'blue'
                        ? 'bg-gradient-to-r from-blue-500 to-indigo-500'
                        : tier.tone === 'purple'
                        ? 'bg-gradient-to-r from-purple-500 to-fuchsia-500'
                        : 'bg-gradient-to-r from-slate-400 to-slate-500'
                    }`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </Card>
            );
          })}
        </div>
      </PageSection>

      <PageSection
        title="User management"
        description="Search, review, and take action on individual accounts."
        icon={<ShieldCheck className="h-6 w-6" />}
        actions={
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              leadingIcon={<RefreshCw className="h-4 w-4" />}
              onClick={loadDashboardData}
            >
              Sync latest
            </Button>
          </div>
        }
      >
        <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div className="relative w-full max-w-md">
            <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              onKeyDown={(event) => event.key === 'Enter' && handleSearch()}
              placeholder="Search by name, email, or tier"
              className="w-full rounded-full border border-slate-200 bg-white/80 px-12 py-3 text-sm text-slate-700 shadow-[0_10px_35px_-25px_rgba(37,99,235,0.6)] focus:border-blue-400 focus:outline-none focus:ring-4 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-900/70 dark:text-slate-100"
            />
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button size="sm" onClick={handleSearch} leadingIcon={<Search className="h-4 w-4" />}>
              Search
            </Button>
            {searchQuery && (
              <Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  setSearchQuery('');
                  loadDashboardData();
                }}
              >
                Clear
              </Button>
            )}
          </div>
        </div>

        <div className="overflow-hidden rounded-3xl border border-white/40 bg-white/70 shadow-[0_32px_90px_-45px_rgba(37,99,235,0.35)] backdrop-blur-xl dark:border-slate-700/60 dark:bg-slate-900/70">
          {loading ? (
            <div className="flex items-center justify-center gap-3 p-10 text-slate-500 dark:text-slate-300">
              <Loader2 className="h-5 w-5 animate-spin" />
              <span>Fetching latest accounts…</span>
            </div>
          ) : users.length === 0 ? (
            <div className="flex h-48 flex-col items-center justify-center gap-2 text-slate-500 dark:text-slate-300">
              <Zap className="h-8 w-8" />
              <p>No users matched your filters.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-white/40 text-left text-sm text-slate-600 dark:divide-slate-700 dark:text-slate-200">
                <thead>
                  <tr className="text-xs uppercase tracking-wide text-slate-400">
                    <th className="px-6 py-4">User</th>
                    <th className="px-6 py-4">Tier</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4">Usage</th>
                    <th className="px-6 py-4">Analyses</th>
                    <th className="px-6 py-4">Joined</th>
                    <th className="px-6 py-4">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/30 dark:divide-slate-800">
                  {users.map((userItem) => {
                    const usagePercentage =
                      userItem.api_calls_limit === -1
                        ? 100
                        : Math.min((userItem.api_calls_used / userItem.api_calls_limit) * 100, 100);

                    return (
                      <tr key={userItem.id} className="transition hover:bg-white/60 dark:hover:bg-slate-900/60">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <span className="flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-500 text-base font-semibold text-white">
                              {userItem.full_name.charAt(0).toUpperCase()}
                            </span>
                            <div>
                              <p className="font-semibold text-slate-800 dark:text-white">{userItem.full_name}</p>
                              <p className="text-xs text-slate-500 dark:text-slate-400">{userItem.email}</p>
                              <div className="mt-1 flex flex-wrap gap-1 text-[10px] font-semibold uppercase tracking-wide text-slate-400">
                                {userItem.is_super_admin && <span className="rounded-full bg-purple-500/15 px-2 py-0.5 text-purple-500">Super admin</span>}
                                {userItem.is_admin && !userItem.is_super_admin && (
                                  <span className="rounded-full bg-blue-500/15 px-2 py-0.5 text-blue-500">Admin</span>
                                )}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <Chip tone={userItem.subscription_tier === 'enterprise' ? 'purple' : userItem.subscription_tier === 'pro' ? 'blue' : 'gray'} size="sm">
                            {userItem.subscription_tier}
                          </Chip>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex flex-col gap-1 text-xs">
                            <span className={`font-semibold ${userItem.is_active ? 'text-emerald-500' : 'text-rose-500'}`}>
                              {userItem.is_active ? '● Active' : '● Inactive'}
                            </span>
                            {userItem.is_premium && <span className="text-amber-500">⭐ Premium</span>}
                            {userItem.is_email_verified && <span className="text-blue-500">✓ Email verified</span>}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-sm font-semibold text-slate-700 dark:text-slate-200">
                            {userItem.api_calls_used.toLocaleString()} / {formatUsageLimit(userItem.api_calls_limit)}
                          </p>
                          <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                            <div
                              className={`h-2 rounded-full ${
                                userItem.api_calls_limit === -1
                                  ? 'bg-gradient-to-r from-emerald-400 to-emerald-500'
                                  : 'bg-gradient-to-r from-blue-500 to-indigo-500'
                              }`}
                              style={{ width: `${usagePercentage}%` }}
                            />
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm font-semibold text-slate-700 dark:text-slate-200">
                          {userItem.total_analyses.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-500 dark:text-slate-300">
                          {formatDate(userItem.created_at)}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex flex-wrap gap-2">
                            <Button size="xs" variant="ghost" onClick={() => handleViewUser(userItem.id)}>
                              View
                            </Button>
                            {user?.is_super_admin && (
                              <>
                                <Button
                                  size="xs"
                                  variant="ghost"
                                  onClick={() => handleTogglePremium(userItem.id)}
                                >
                                  {userItem.is_premium ? 'Remove premium' : 'Make premium'}
                                </Button>
                                <Button
                                  size="xs"
                                  variant="ghost"
                                  onClick={() => handleResetUsage(userItem.id)}
                                >
                                  Reset usage
                                </Button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </PageSection>

      {showUserModal && selectedUser && (
        <div className="fixed inset-0 z-[120] flex items-center justify-center bg-slate-950/80 px-4 py-10 backdrop-blur">
          <div className="relative w-full max-w-2xl overflow-hidden rounded-3xl border border-white/10 bg-white/10 p-6 shadow-[0_50px_120px_-60px_rgba(99,102,241,0.6)] backdrop-blur-xl dark:bg-slate-900/80">
            <button
              onClick={() => setShowUserModal(false)}
              className="absolute right-6 top-6 rounded-full bg-white/10 p-2 text-white transition hover:bg-white/20"
              aria-label="Close"
            >
              <X className="h-4 w-4" />
            </button>

            <div className="flex items-center gap-4 pb-6">
              <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-500 text-2xl font-semibold text-white">
                {selectedUser.full_name.charAt(0).toUpperCase()}
              </span>
              <div>
                <h3 className="text-2xl font-semibold text-white">{selectedUser.full_name}</h3>
                <p className="text-sm text-slate-300">{selectedUser.email}</p>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {[
                { label: 'User ID', value: selectedUser.id },
                { label: 'Username', value: selectedUser.username },
                { label: 'Subscription', value: selectedUser.subscription_tier },
                { label: 'Status', value: selectedUser.is_active ? 'Active' : 'Inactive' },
                { label: 'API used', value: selectedUser.api_calls_used.toLocaleString() },
                { label: 'API limit', value: formatUsageLimit(selectedUser.api_calls_limit) },
                { label: 'Analyses', value: selectedUser.total_analyses.toLocaleString() },
                { label: 'Created', value: formatDate(selectedUser.created_at) },
              ].map((row) => (
                <Card key={row.label} variant="translucent" padding="md" className="bg-white/5 text-slate-200">
                  <p className="text-[11px] uppercase tracking-wide text-slate-400">{row.label}</p>
                  <p className="mt-2 text-sm font-semibold text-white">{row.value ?? '—'}</p>
                </Card>
              ))}
            </div>

            <div className="mt-6 flex flex-wrap items-center gap-2 text-xs">
              {selectedUser.is_active && <Chip tone="emerald" size="sm">Active</Chip>}
              {selectedUser.is_premium && <Chip tone="amber" size="sm">Premium</Chip>}
              {selectedUser.is_email_verified && <Chip tone="blue" size="sm">Email verified</Chip>}
              {selectedUser.is_admin && <Chip tone="purple" size="sm">Admin</Chip>}
              {selectedUser.is_super_admin && <Chip tone="purple" size="sm">Super admin</Chip>}
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
};

export default AdminPage;