import React, { useMemo, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ArrowRight, Eye, EyeOff, Mail, Shield, Sparkles, User, UserPlus } from 'lucide-react';
import PageContainer from '../components/page/PageContainer';
import PageHeader from '../components/PageHeader';
import PageSection from '../components/page/PageSection';
import Card from '../components/ui/Card';
import Chip from '../components/ui/Chip';
import { Button } from '../components/ui/Button';
import GoogleSignInButton from '../components/GoogleSignInButton';
import { useAuth } from '../hooks/useAuth';

const inputClasses =
  'w-full rounded-2xl border border-gray-200/70 bg-white/80 px-4 py-3 text-sm font-medium text-gray-800 shadow-[0_15px_35px_-25px_rgba(129,140,248,0.45)] transition focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-200 dark:border-slate-700/60 dark:bg-slate-900/70 dark:text-slate-100 dark:shadow-[0_18px_40px_-30px_rgba(15,23,42,0.8)] dark:focus:border-indigo-400 dark:focus:ring-indigo-500/40';

const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { signup } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    username: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const offerContext = location.state as { planName?: string; studentDiscount?: boolean } | undefined;

  const onboardingHighlights = useMemo(
    () => [
      {
        icon: <UserPlus className="h-5 w-5 text-blue-500" />,
        title: '3-day premium trial',
        description: 'Explore Pro features without providing a card upfront.',
      },
      {
        icon: <Shield className="h-5 w-5 text-emerald-500" />,
        title: 'Privacy-first orchestration',
        description: 'Uploads are encrypted in-flight and never stored after processing.',
      },
      {
        icon: <Sparkles className="h-5 w-5 text-purple-500" />,
        title: 'Creative insights',
        description: 'Get full prompt breakdowns, lighting, materials, and frame analytics.',
      },
    ],
    []
  );

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsLoading(true);
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    try {
      await signup({
        email: formData.email,
        password: formData.password,
        full_name: formData.fullName,
        username: formData.username,
      });
      navigate('/verify-email', { state: { email: formData.email } });
    } catch (submissionError: unknown) {
      const message = submissionError instanceof Error ? submissionError.message : 'Signup failed';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PageContainer>
      <PageHeader
        title="Create your workspace"
        subtitle="Spin up a secure Prompt Detective account, invite collaborators, and start reverse-engineering prompts with cinematic clarity."
        breadcrumbs={[{ label: 'Account', href: '/signup' }, { label: 'Create account' }]}
        primaryAction={{ label: 'View pricing', onClick: () => navigate('/pricing') }}
        secondaryAction={{ label: 'Sign in', onClick: () => navigate('/login') }}
        illustration={<User className="h-12 w-12 text-indigo-500" />}
      />

      <div className="grid gap-6 xl:grid-cols-[1.05fr,0.95fr]">
        <PageSection
          title="Included with every account"
          description="A thoughtful onboarding experience designed for indie creators, studios, and research teams alike."
          icon={<Sparkles className="h-6 w-6" />}
          variant="translucent"
        >
          <div className="grid gap-4 md:grid-cols-2">
            {onboardingHighlights.map((item) => (
              <Card key={item.title} variant="outline" padding="md" className="flex h-full flex-col gap-3 bg-white/85 dark:bg-slate-900/70">
                <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 dark:bg-indigo-500/10">
                  {item.icon}
                </span>
                <p className="text-lg font-semibold text-gray-900 dark:text-slate-100">{item.title}</p>
                <p className="text-sm text-gray-500 dark:text-slate-400">{item.description}</p>
              </Card>
            ))}
          </div>

          <div className="mt-6 space-y-3 rounded-3xl border border-white/60 bg-white/70 p-6 shadow-[0_18px_45px_-25px_rgba(129,140,248,0.45)] dark:border-white/5 dark:bg-slate-900/70 dark:shadow-[0_18px_50px_-25px_rgba(15,23,42,0.65)]">
            <Chip tone="purple" size="sm">Welcome kit</Chip>
            <div className="flex flex-col gap-2 text-sm text-gray-600 dark:text-slate-300 sm:flex-row sm:justify-between">
              <span>Unlock three premium analyses plus our onboarding checklist the moment you activate.</span>
              <span className="font-semibold text-blue-600 dark:text-indigo-300">Invite teammates anytime →</span>
            </div>
          </div>
        </PageSection>

        <PageSection
          title="Finish creating your account"
          description={offerContext?.planName ? `You're moments away from activating the ${offerContext.planName} plan.` : 'Set your credentials and we will guide you through verification.'}
          icon={<Mail className="h-6 w-6" />}
        >
          <Card variant="elevated" padding="lg" className="space-y-6 bg-white/90 dark:bg-slate-900/85">
            <form className="space-y-5" onSubmit={handleSubmit}>
              <div className="grid gap-4 md:grid-cols-2">
                <label className="space-y-2 text-sm font-semibold text-gray-700 dark:text-slate-200">
                  Full name
                  <input
                    id="fullName"
                    name="fullName"
                    type="text"
                    required
                    placeholder="Alex Rivera"
                    className={inputClasses}
                    value={formData.fullName}
                    onChange={handleChange}
                  />
                </label>
                <label className="space-y-2 text-sm font-semibold text-gray-700 dark:text-slate-200">
                  Username <span className="font-normal text-gray-400 dark:text-slate-500">(optional)</span>
                  <input
                    id="username"
                    name="username"
                    type="text"
                    placeholder="studio-alex"
                    className={inputClasses}
                    value={formData.username}
                    onChange={handleChange}
                  />
                </label>
              </div>

              <label className="space-y-2 text-sm font-semibold text-gray-700 dark:text-slate-200">
                Email address
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  placeholder="you@brand.co"
                  className={inputClasses}
                  value={formData.email}
                  onChange={handleChange}
                />
              </label>

              <div className="grid gap-4 md:grid-cols-2">
                <label className="space-y-2 text-sm font-semibold text-gray-700 dark:text-slate-200">
                  Password
                  <div className="relative">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      autoComplete="new-password"
                      required
                      placeholder="Create a password"
                      className={`${inputClasses} pr-12`}
                      value={formData.password}
                      onChange={handleChange}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword((prev) => !prev)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-2 text-gray-400 transition hover:text-gray-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-300 dark:text-slate-500 dark:hover:text-slate-300"
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      aria-pressed={showPassword}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </label>
                <label className="space-y-2 text-sm font-semibold text-gray-700 dark:text-slate-200">
                  Confirm password
                  <div className="relative">
                    <input
                      id="confirmPassword"
                      name="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      autoComplete="new-password"
                      required
                      placeholder="Repeat password"
                      className={`${inputClasses} pr-12`}
                      value={formData.confirmPassword}
                      onChange={handleChange}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword((prev) => !prev)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-2 text-gray-400 transition hover:text-gray-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-300 dark:text-slate-500 dark:hover:text-slate-300"
                      aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                      aria-pressed={showConfirmPassword}
                    >
                      {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </label>
              </div>

              <div className="rounded-2xl border border-blue-200/60 bg-blue-50/70 p-4 text-xs text-blue-700 dark:border-indigo-400/30 dark:bg-indigo-500/10 dark:text-indigo-200">
                <p className="text-sm font-semibold">Password tips</p>
                <ul className="mt-2 space-y-1">
                  <li>• At least 8 characters</li>
                  <li>• Include upper & lowercase letters</li>
                  <li>• Add a number or symbol for extra strength</li>
                </ul>
              </div>

              {error && (
                <div className="rounded-2xl border border-rose-200/60 bg-rose-50/70 px-4 py-3 text-sm text-rose-600 dark:border-rose-500/40 dark:bg-rose-500/10 dark:text-rose-200">
                  {error}
                </div>
              )}

              <Button type="submit" size="lg" fullWidth isLoading={isLoading} leadingIcon={<ArrowRight className="h-4 w-4" />}>
                {isLoading ? 'Creating workspace…' : 'Create account'}
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
              buttonText="Sign up with Google"
              onSuccess={() => navigate('/dashboard')}
              onError={(message) => setError(message)}
              className="rounded-2xl border-gray-200/70 bg-white/80 py-3 text-sm font-semibold shadow-[0_15px_35px_-25px_rgba(129,140,248,0.45)] hover:bg-white dark:border-slate-700/60 dark:bg-slate-900/70 dark:text-slate-100"
            />

            <div className="rounded-2xl border border-gray-200/70 bg-white/60 p-4 text-sm text-gray-600 dark:border-slate-700/60 dark:bg-slate-900/70 dark:text-slate-300">
              <p className="font-semibold text-gray-800 dark:text-slate-100">Already have an account?</p>
              <p className="mt-1">
                Sign in to access your dashboard and history.
                <Link to="/login" className="ml-1 font-semibold text-blue-600 transition hover:text-blue-500 dark:text-indigo-300 dark:hover:text-indigo-200">
                  Return to login
                </Link>
              </p>
            </div>
          </Card>
        </PageSection>
      </div>
    </PageContainer>
  );
};

export default SignupPage;