import React, { useEffect, useMemo, useState } from 'react';
import { Calendar, CheckCircle, Edit, KeyRound, Loader2, Lock, Mail, ShieldCheck, Trash2, User, Zap, AlertTriangle } from 'lucide-react';
import PageContainer from '../components/page/PageContainer';
import PageHeader from '../components/PageHeader';
import PageSection from '../components/page/PageSection';
import Card from '../components/ui/Card';
import Chip from '../components/ui/Chip';
import { Button } from '../components/ui/Button';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';

const inputClasses =
  'w-full rounded-2xl border border-gray-200/70 bg-white/85 px-4 py-3 text-sm font-medium text-gray-800 shadow-[0_12px_32px_-24px_rgba(59,130,246,0.45)] transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-200 dark:border-slate-700/60 dark:bg-slate-900/70 dark:text-slate-100 dark:shadow-[0_18px_45px_-32px_rgba(15,23,42,0.85)] dark:focus:border-indigo-400 dark:focus:ring-indigo-500/40';

const ProfilePage: React.FC = () => {
  const { user, updateProfile, deleteAccount } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    username: user?.username || '',
    email: user?.email || '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState('');
  const [deleteError, setDeleteError] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  const stats = useMemo(() => {
    if (!user) {
      return [];
    }

    return [
      {
        label: 'Subscription tier',
        value: user.subscription_tier ? user.subscription_tier.charAt(0).toUpperCase() + user.subscription_tier.slice(1) : 'Free',
        tone: 'blue' as const,
        icon: <ShieldCheck className="h-5 w-5 text-blue-500" />,
      },
      {
        label: 'API usage',
        value: `${user.api_calls_used ?? 0} / ${user.api_calls_limit ?? 0}`,
        tone: 'purple' as const,
        icon: <Zap className="h-5 w-5 text-purple-500" />,
      },
      {
        label: 'Member since',
        value:
          user.created_at && user.created_at !== 'Invalid Date'
            ? new Date(user.created_at).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })
            : 'Recently',
        tone: 'emerald' as const,
        icon: <Calendar className="h-5 w-5 text-emerald-500" />,
      },
    ];
  }, [user]);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setFormData((previous) => ({ ...previous, [name]: value }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      await updateProfile(formData);
      setMessage('Profile updated successfully.');
      setIsEditing(false);
      toast.success('Profile updated successfully.');
    } catch (error: unknown) {
      const detail = error instanceof Error ? error.message : 'Failed to update profile. Please try again later.';
      setMessage(detail);
      toast.error(detail);
    } finally {
      setIsLoading(false);
    }
  };

  const requiredDeletePhrase = user?.email ?? '';

  const openDeleteModal = () => {
    setDeleteConfirmation('');
    setDeleteError('');
    setIsDeleteModalOpen(true);
  };

  const closeDeleteModal = () => {
    setIsDeleteModalOpen(false);
    setDeleteConfirmation('');
    setDeleteError('');
  };

  useEffect(() => {
    if (!isDeleteModalOpen) return;

    const handler = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        closeDeleteModal();
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isDeleteModalOpen]);

  const handleConfirmDelete = async () => {
    if (!user?.email) {
      setDeleteError('We could not determine your account email. Please refresh and try again.');
      return;
    }

    if (deleteConfirmation.trim().toLowerCase() !== user.email.toLowerCase()) {
      setDeleteError('Type your account email exactly to confirm deletion.');
      return;
    }

    setIsDeleting(true);
    setDeleteError('');

    try {
      await deleteAccount();
      toast.success('Your account has been deleted. We hope to see you again.');
      closeDeleteModal();
      window.location.href = '/';
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete account. Please try again.';
      setDeleteError(message);
      toast.error(message);
    } finally {
      setIsDeleting(false);
    }
  };

  if (!user) {
    return (
      <PageContainer>
        <PageHeader
          title="Profile access restricted"
          subtitle="Log in to view and edit your Prompt Detective profile, usage stats, and security preferences."
          breadcrumbs={[{ label: 'Account', href: '/login' }, { label: 'Profile' }]}
          illustration={<Lock className="h-12 w-12 text-indigo-500" />}
        />
        <PageSection title="Authentication required" description="You need an active session to view this page." icon={<KeyRound className="h-6 w-6" />}>
          <Card variant="elevated" padding="lg" className="flex flex-col gap-4 bg-white/90 text-sm text-gray-600 dark:bg-slate-900/80 dark:text-slate-300">
            <p>Your session might have expired. Jump back to the login screen and we will redirect you here once you’re authenticated.</p>
            <Button onClick={() => window.location.assign('/login')} leadingIcon={<Lock className="h-4 w-4" />}>
              Go to login
            </Button>
          </Card>
        </PageSection>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageHeader
        title="Profile & preferences"
        subtitle="Fine-tune your personal details, manage workspace credentials, and understand how your team is using Prompt Detective."
        breadcrumbs={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'Profile' }]}
        primaryAction={{ label: isEditing ? 'Cancel editing' : 'Edit profile', onClick: () => setIsEditing((previous) => !previous) }}
        secondaryAction={{ label: 'View usage history', onClick: () => window.location.assign('/history') }}
        illustration={<User className="h-12 w-12 text-indigo-500" />}
      />

      <div className="grid gap-6 lg:grid-cols-[1.05fr,0.95fr]">
        <PageSection
          title="Account overview"
          description="A quick snapshot of your subscription status, usage, and onboarding timeline."
          icon={<ShieldCheck className="h-6 w-6" />}
          variant="translucent"
        >
          <div className="grid gap-4 md:grid-cols-3">
            {stats.map((item) => (
              <Card key={item.label} variant="outline" padding="md" className="flex h-full flex-col gap-3 bg-white/85 dark:bg-slate-900/70">
                <div className="flex items-center justify-between">
                  <span className="text-xs uppercase tracking-wide text-gray-400 dark:text-slate-500">{item.label}</span>
                  {item.icon}
                </div>
                <p className="text-2xl font-semibold text-gray-900 dark:text-slate-100">{item.value}</p>
                <Chip tone={item.tone} size="sm">Live sync</Chip>
              </Card>
            ))}
          </div>

          <div className="mt-6 grid gap-3 text-sm text-gray-500 dark:text-slate-400 sm:grid-cols-2">
            <div className="flex items-center gap-3 rounded-2xl border border-gray-200/60 bg-white/80 px-4 py-3 dark:border-slate-700/60 dark:bg-slate-900/70">
              <CheckCircle className="h-4 w-4 text-emerald-500" />
              <span>Email and usage data stay encrypted in transit and at rest.</span>
            </div>
            <div className="flex items-center gap-3 rounded-2xl border border-gray-200/60 bg-white/80 px-4 py-3 dark:border-slate-700/60 dark:bg-slate-900/70">
              <Mail className="h-4 w-4 text-blue-500" />
              <span>Update contact details anytime—billing receipts follow automatically.</span>
            </div>
          </div>
        </PageSection>

        <PageSection
          title="Personal information"
          description="Edit your identity, handle, or contact email. Changes apply instantly across Prompt Detective."
          icon={<Edit className="h-6 w-6" />}
        >
          <Card variant="elevated" padding="lg" className="space-y-6 bg-white/90 dark:bg-slate-900/85">
            {message && (
              <div
                className={`rounded-2xl border px-4 py-3 text-sm ${
                  message.toLowerCase().includes('success')
                    ? 'border-emerald-300 bg-emerald-50/80 text-emerald-600 dark:border-emerald-400/40 dark:bg-emerald-500/10 dark:text-emerald-200'
                    : 'border-rose-300 bg-rose-50/80 text-rose-600 dark:border-rose-500/40 dark:bg-rose-500/10 dark:text-rose-200'
                }`}
              >
                {message}
              </div>
            )}

            <form className="space-y-5" onSubmit={handleSubmit}>
              <div className="space-y-2">
                <label htmlFor="full_name" className="text-sm font-semibold text-gray-700 dark:text-slate-200">
                  Full name
                </label>
                <input
                  id="full_name"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  disabled={!isEditing || isLoading}
                  className={inputClasses}
                  placeholder="Your name"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="username" className="text-sm font-semibold text-gray-700 dark:text-slate-200">
                  Username
                </label>
                <input
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  disabled={!isEditing || isLoading}
                  className={inputClasses}
                  placeholder="@handle"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-semibold text-gray-700 dark:text-slate-200">
                  Email address
                </label>
                <input
                  id="email"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  disabled={!isEditing || isLoading}
                  className={inputClasses}
                  placeholder="you@company.com"
                />
              </div>

              <div className="flex justify-end gap-3">
                {isEditing ? (
                  <>
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={() => {
                        setIsEditing(false);
                        setMessage('');
                        setFormData({
                          full_name: user.full_name || '',
                          username: user.username || '',
                          email: user.email || '',
                        });
                      }}
                    >
                      Cancel
                    </Button>
                    <Button type="submit" isLoading={isLoading} leadingIcon={<CheckCircle className="h-4 w-4" />}>
                      {isLoading ? 'Saving…' : 'Save changes'}
                    </Button>
                  </>
                ) : (
                  <Button type="button" onClick={() => setIsEditing(true)} leadingIcon={<Edit className="h-4 w-4" />}>
                    Edit profile
                  </Button>
                )}
              </div>
            </form>

            <div className="rounded-2xl border border-gray-200/70 bg-white/60 p-4 text-xs text-gray-500 dark:border-slate-700/60 dark:bg-slate-900/70 dark:text-slate-300">
              <p className="text-sm font-semibold text-gray-800 dark:text-slate-100">Security reminder</p>
              <p className="mt-1">
                Changing your email automatically revokes all API keys and requires re-verification the next time you log in.
              </p>
            </div>
          </Card>
        </PageSection>
      </div>

      <PageSection
        title="Security controls"
        description="Strengthen workspace access, explore API hygiene, and learn how to remove your account."
        icon={<Lock className="h-6 w-6" />}
      >
        <div className="grid gap-6 lg:grid-cols-3">
          <Card variant="outline" padding="lg" className="flex h-full flex-col gap-4 bg-white/85 dark:bg-slate-900/70">
            <Chip tone="purple" size="sm">API hygiene</Chip>
            <p className="text-base font-semibold text-gray-900 dark:text-slate-100">Rotate API keys every 30 days.</p>
            <p className="text-sm text-gray-600 dark:text-slate-300">
              Head to the dashboard’s API Keys tab whenever you update your email or spot unusual usage.
            </p>
            <Button variant="ghost" size="sm" onClick={() => window.location.assign('/dashboard')}>
              Manage API keys
            </Button>
          </Card>

          <Card variant="outline" padding="lg" className="flex h-full flex-col gap-4 bg-white/85 dark:bg-slate-900/70">
            <Chip tone="blue" size="sm">Two-factor soon</Chip>
            <p className="text-base font-semibold text-gray-900 dark:text-slate-100">Email OTPs today, authenticator apps tomorrow.</p>
            <p className="text-sm text-gray-600 dark:text-slate-300">
              We are rolling out app-based MFA shortly. Early adopters get priority—opt-in via tryreverseai@gmail.com.
            </p>
            <Button variant="ghost" size="sm" onClick={() => window.location.assign('mailto:tryreverseai@gmail.com')}>
              Request MFA beta
            </Button>
          </Card>

          <Card variant="outline" padding="lg" className="flex h-full flex-col gap-4 bg-rose-50/70 dark:bg-rose-500/10">
            <Chip tone="rose" size="sm">Danger zone</Chip>
            <p className="text-base font-semibold text-rose-600 dark:text-rose-200">Permanently delete your account.</p>
            <p className="text-sm text-rose-600 dark:text-rose-200">
              This action removes usage history, analyses, and API credentials instantly. There is no undo.
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={openDeleteModal}
              className="border-rose-400 text-rose-600 hover:bg-rose-100 dark:border-rose-400/60 dark:text-rose-200 dark:hover:bg-rose-500/10"
              leadingIcon={<Trash2 className="h-4 w-4" />}
            >
              Delete account
            </Button>
          </Card>
        </div>
      </PageSection>

      {isDeleteModalOpen && (
        <div className="fixed inset-0 z-[120] flex items-center justify-center bg-slate-950/70 px-4 py-8 backdrop-blur-md">
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-account-title"
            className="relative w-full max-w-lg rounded-3xl border border-rose-200/40 bg-white/95 p-8 shadow-[0_28px_80px_-40px_rgba(244,63,94,0.35)] dark:border-rose-500/20 dark:bg-slate-950/90 dark:shadow-[0_28px_80px_-40px_rgba(244,63,94,0.2)]"
          >
            <button
              type="button"
              onClick={closeDeleteModal}
              className="absolute right-4 top-4 rounded-full bg-rose-100/70 px-3 py-1 text-xs font-semibold text-rose-600 transition hover:bg-rose-200/80 dark:bg-rose-500/10 dark:text-rose-200 dark:hover:bg-rose-500/20"
            >
              Cancel
            </button>

            <div className="flex items-center gap-3">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-100 text-rose-600 dark:bg-rose-500/10 dark:text-rose-200">
                <AlertTriangle className="h-6 w-6" />
              </span>
              <div>
                <h2 id="delete-account-title" className="text-xl font-semibold text-rose-700 dark:text-rose-200">
                  Permanently delete your account
                </h2>
                <p className="text-sm text-rose-600/90 dark:text-rose-200/80">
                  This removes your profile, analyses, API keys, and billing history immediately. There is no undo.
                </p>
              </div>
            </div>

            <div className="mt-6 space-y-4 rounded-2xl border border-rose-200/60 bg-rose-50/60 p-5 text-sm text-rose-700 dark:border-rose-500/30 dark:bg-rose-500/5 dark:text-rose-100">
              <p className="font-semibold">Before you continue</p>
              <ul className="space-y-2 text-sm">
                <li>• Export any prompts or invoices you need for compliance.</li>
                <li>• Active subscriptions and credit packs will be cancelled instantly.</li>
                <li>• You can rejoin anytime, but previous data cannot be restored.</li>
              </ul>
            </div>

            <div className="mt-6 space-y-2">
              <label htmlFor="delete-confirm" className="text-sm font-semibold text-rose-700 dark:text-rose-100">
                Type <span className="font-mono">{requiredDeletePhrase}</span> to confirm
              </label>
              <input
                id="delete-confirm"
                value={deleteConfirmation}
                onChange={(event) => setDeleteConfirmation(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter') {
                    event.preventDefault();
                    void handleConfirmDelete();
                  }
                }}
                placeholder={requiredDeletePhrase}
                className="w-full rounded-2xl border border-rose-200/70 bg-white/90 px-4 py-3 text-sm font-medium text-rose-700 shadow-inner shadow-rose-100 focus:border-rose-500 focus:outline-none focus:ring-2 focus:ring-rose-200 dark:border-rose-500/30 dark:bg-slate-900/70 dark:text-rose-100 dark:focus:border-rose-400 dark:focus:ring-rose-400/40"
                autoFocus
              />
              <p className="text-xs text-rose-500 dark:text-rose-200/70">
                We require this manual step to prevent accidental deletions.
              </p>
            </div>

            {deleteError && (
              <div className="mt-4 flex items-start gap-2 rounded-2xl border border-rose-300/60 bg-rose-50/70 px-4 py-3 text-sm text-rose-700 dark:border-rose-500/40 dark:bg-rose-500/10 dark:text-rose-200">
                <AlertTriangle className="mt-0.5 h-4 w-4" />
                <span>{deleteError}</span>
              </div>
            )}

            <div className="mt-8 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
              <Button variant="ghost" onClick={closeDeleteModal} disabled={isDeleting}>
                Keep my account
              </Button>
              <Button
                type="button"
                onClick={() => void handleConfirmDelete()}
                disabled={isDeleting || deleteConfirmation.trim().length === 0}
                className="bg-rose-600 hover:bg-rose-700 dark:bg-rose-500 dark:hover:bg-rose-400"
                leadingIcon={isDeleting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
              >
                {isDeleting ? 'Deleting…' : 'Delete account now'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
};

export default ProfilePage;