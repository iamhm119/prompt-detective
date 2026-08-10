import React, { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, Eye, EyeOff, Lock, Mail, ShieldCheck, Sparkles, Zap } from 'lucide-react';
import PageContainer from '../components/page/PageContainer';
import PageHeader from '../components/PageHeader';
import PageSection from '../components/page/PageSection';
import Card from '../components/ui/Card';
import Chip from '../components/ui/Chip';
import { Button } from '../components/ui/Button';
import GoogleSignInButton from '../components/GoogleSignInButton';
import { useAuth } from '../hooks/useAuth';

const inputClasses =
  'w-full rounded-2xl border border-gray-200/70 bg-white/80 px-4 py-3 text-sm font-medium text-gray-800 shadow-[0_15px_35px_-25px_rgba(59,130,246,0.45)] transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-200 dark:border-slate-700/60 dark:bg-slate-900/70 dark:text-slate-100 dark:shadow-[0_18px_40px_-30px_rgba(15,23,42,0.8)] dark:focus:border-indigo-400 dark:focus:ring-indigo-500/40';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const highlights = useMemo(
    () => [
      {
        label: 'Prompt reconstruction',
        tone: 'blue' as const,
        description: 'Accurate prompts with style, lighting, and camera notes in seconds.',
      },
      {
        label: 'Video intelligence',
        tone: 'purple' as const,
        description: 'Frame-by-frame breakdowns for dynamic sequences up to 5 minutes long.',
      },
      {
        label: 'Enterprise security',
        tone: 'emerald' as const,
        description: 'SOC2-ready encryption and zero-persistence uploads for peace of mind.',
      },
    ],
    []
  );

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await login({ email, password });
      navigate('/dashboard');
    } catch (submissionError: unknown) {
      const message = submissionError instanceof Error ? submissionError.message : 'Login failed';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PageContainer>
      <PageHeader
        title="Welcome back"
        subtitle="Sign in to keep reverse-engineering media, export beautiful prompt bundles, and sync analytics across your team."
        breadcrumbs={[{ label: 'Account', href: '/login' }, { label: 'Sign in' }]}
        primaryAction={{ label: 'Create account', onClick: () => navigate('/signup') }}
        secondaryAction={{ label: 'Pricing & plans', onClick: () => navigate('/pricing') }}
        illustration={<Sparkles className="h-12 w-12 text-indigo-500" />}
      />

      <div className="grid gap-6 lg:grid-cols-[1.05fr,0.95fr]">
        <PageSection
          title="Why Prompt Detective"
          description="A polished sign-in flow built for creators, product teams, and studios who need trustworthy prompt intelligence."
          icon={<ShieldCheck className="h-6 w-6" />}
          variant="translucent"
        >
          <div className="grid gap-5 md:grid-cols-2">
            {highlights.map((item) => (
              <Card key={item.label} variant="outline" padding="md" className="flex h-full flex-col gap-3 bg-white/85 dark:bg-slate-900/70">
                <Chip tone={item.tone} size="sm">{item.label}</Chip>
                <p className="text-base font-semibold text-gray-900 dark:text-slate-100">{item.description}</p>
                <span className="text-xs uppercase tracking-wide text-gray-400 dark:text-slate-500">Included in all plans</span>
              </Card>
            ))}
          </div>
          <div className="mt-6 grid gap-3 text-sm text-gray-500 dark:text-slate-400 sm:grid-cols-2">
            <div className="flex items-center gap-3 rounded-2xl border border-gray-200/60 bg-white/80 px-4 py-3 dark:border-slate-700/60 dark:bg-slate-900/70">
              <Zap className="h-4 w-4 text-amber-500" />
              <span>Average analysis turnaround under 90 seconds</span>
            </div>
            <div className="flex items-center gap-3 rounded-2xl border border-gray-200/60 bg-white/80 px-4 py-3 dark:border-slate-700/60 dark:bg-slate-900/70">
              <Lock className="h-4 w-4 text-blue-500" />
              <span>Zero-retention uploads with in-flight encryption</span>
            </div>
          </div>
        </PageSection>

        <PageSection
          title="Sign in"
          description="Access your dashboard, prompt history, and team workspace."
          icon={<Lock className="h-6 w-6" />}
        >
          <Card variant="elevated" padding="lg" className="space-y-6 bg-white/90 dark:bg-slate-900/85">
            <form className="space-y-5" onSubmit={handleSubmit}>
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-semibold text-gray-700 dark:text-slate-200">Email</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                  <input
                    id="email"
                    type="email"
                    autoComplete="email"
                    required
                    className={`${inputClasses} pl-11`}
                    placeholder="you@studio.co"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-semibold text-gray-700 dark:text-slate-200">Password</label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    className={`${inputClasses} pl-11 pr-12`}
                    placeholder="Enter your password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-2 text-gray-400 transition hover:text-gray-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-300 dark:text-slate-500 dark:hover:text-slate-300"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    aria-pressed={showPassword}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
                <label className="inline-flex cursor-pointer items-center gap-3 text-gray-600 dark:text-slate-300">
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-gray-300 text-blue-500 focus:ring-blue-200 dark:border-slate-600 dark:bg-slate-900"
                  />
                  Remember this device
                </label>
                <Link to="/forgot-password" className="font-semibold text-blue-600 hover:text-blue-500 dark:text-indigo-300 dark:hover:text-indigo-200">
                  Forgot password?
                </Link>
              </div>

              {error && (
                <div className="rounded-2xl border border-rose-200/60 bg-rose-50/70 px-4 py-3 text-sm text-rose-600 dark:border-rose-500/40 dark:bg-rose-500/10 dark:text-rose-200">
                  {error}
                </div>
              )}

              <Button type="submit" size="lg" fullWidth isLoading={isLoading} leadingIcon={<ArrowRight className="h-4 w-4" />}>
                {isLoading ? 'Signing in…' : 'Access dashboard'}
              </Button>
            </form>

            <div className="relative">
              <div className="absolute inset-0 flex items-center" aria-hidden="true">
                <span className="w-full border-t border-gray-200 dark:border-slate-700" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-transparent px-2 text-gray-400 dark:text-slate-500">Or continue with</span>
              </div>
            </div>

            <GoogleSignInButton
              buttonText="Sign in with Google"
              onSuccess={() => navigate('/dashboard')}
              onError={(message) => setError(message)}
              className="rounded-2xl border-gray-200/70 bg-white/80 py-3 text-sm font-semibold shadow-[0_15px_35px_-25px_rgba(59,130,246,0.45)] hover:bg-white dark:border-slate-700/60 dark:bg-slate-900/70 dark:text-slate-100"
            />

            <div className="rounded-2xl border border-gray-200/70 bg-white/60 p-4 text-sm text-gray-600 dark:border-slate-700/60 dark:bg-slate-900/70 dark:text-slate-300">
              <p className="font-semibold text-gray-800 dark:text-slate-100">New here?</p>
              <p className="mt-1">
                Start with the free tier or explore premium prompts for three days on the house.
                <Link to="/signup" className="ml-1 font-semibold text-blue-600 transition hover:text-blue-500 dark:text-indigo-300 dark:hover:text-indigo-200">
                  Create an account
                </Link>
              </p>
            </div>
          </Card>
        </PageSection>
      </div>
    </PageContainer>
  );
};

export default LoginPage;