import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle,
  Clock,
  KeyRound,
  Lock,
  Mail,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Eye,
  EyeOff,
} from 'lucide-react';
import axios from 'axios';
import OTPInput from '../components/OTPInput';
import PageContainer from '../components/page/PageContainer';
import PageHeader from '../components/PageHeader';
import PageSection from '../components/page/PageSection';
import Card from '../components/ui/Card';
import Chip from '../components/ui/Chip';
import { Button } from '../components/ui/Button';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const inputClasses =
  'w-full rounded-2xl border border-gray-200/70 bg-white/85 px-4 py-3 text-sm font-medium text-gray-800 shadow-[0_15px_35px_-25px_rgba(59,130,246,0.45)] transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-200 dark:border-slate-700/60 dark:bg-slate-900/70 dark:text-slate-100 dark:shadow-[0_18px_40px_-30px_rgba(15,23,42,0.8)] dark:focus:border-indigo-400 dark:focus:ring-indigo-500/40';

type Step = 'email' | 'otp' | 'password' | 'success';
const OTP_LENGTH = 6;
const EMPTY_OTP = ' '.repeat(OTP_LENGTH);

const ForgotPasswordPage: React.FC = () => {
  const navigate = useNavigate();

  const [step, setStep] = useState<Step>('email');
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState(EMPTY_OTP);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [resendDisabled, setResendDisabled] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const normalizedOtp = useMemo(() => otp.replace(/\D/g, ''), [otp]);

  const insights = useMemo(
    () => [
      {
        label: 'Safe reset pipeline',
        tone: 'blue' as const,
        description: 'Every code expires in minutes and is hashed at rest to block interception attempts.',
      },
      {
        label: 'Zero credential reuse',
        tone: 'purple' as const,
        description: 'Prompts to use unique passwords and surfaces password strength tips right in flow.',
      },
      {
        label: 'Global email delivery',
        tone: 'emerald' as const,
        description: 'Optimised SMTP routing across Mumbai, Frankfurt, and Oregon for speedy delivery.',
      },
    ],
    []
  );

  const timeline = useMemo(
    () => [
      { id: 'email' as Step, title: 'Request reset code', meta: 'Confirm the account that needs a password refresh.' },
      { id: 'otp' as Step, title: 'Verify OTP', meta: 'We email a 6-digit code that expires in two minutes.' },
      { id: 'password' as Step, title: 'Set a new password', meta: 'Create a strong, unique password to secure your workspace.' },
      { id: 'success' as Step, title: 'Done', meta: 'Jump back into Prompt Detective with your new credentials.' },
    ],
    []
  );

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown((value) => value - 1), 1000);
      return () => clearTimeout(timer);
    }
    setResendDisabled(false);
    return undefined;
  }, [countdown]);

  const handleVerifyOTP = useCallback(async () => {
    if (normalizedOtp.length !== OTP_LENGTH) {
      setError('Please enter the six-digit code we emailed you.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await axios.post(`${API_BASE_URL}/auth/password-reset/verify-otp`, {
        email,
        otp_code: normalizedOtp,
      });
      setStep('password');
    } catch (verificationError: unknown) {
      const message =
        typeof verificationError === 'object' && verificationError && 'response' in verificationError
          ? (verificationError as any).response?.data?.detail
          : undefined;
      setError(message || 'Invalid code. Please try again.');
      setOtp(EMPTY_OTP);
    } finally {
      setLoading(false);
    }
  }, [email, normalizedOtp, otp]);

  useEffect(() => {
    if (step === 'otp' && normalizedOtp.length === OTP_LENGTH && !loading) {
      void handleVerifyOTP();
    }
  }, [handleVerifyOTP, loading, normalizedOtp, step]);

  const handleRequestOTP = useCallback(
    async (event: React.FormEvent) => {
      event.preventDefault();
      setLoading(true);
      setError('');

      try {
  await axios.post(`${API_BASE_URL}/auth/password-reset/request`, { email });
  setOtp(EMPTY_OTP);
        setPassword('');
        setConfirmPassword('');
        setStep('otp');
        setResendDisabled(true);
        setCountdown(120);
      } catch (requestError: unknown) {
        const message =
          typeof requestError === 'object' && requestError && 'response' in requestError
            ? (requestError as any).response?.data?.detail
            : undefined;
        setError(message || 'Failed to send reset code. Please try again.');
      } finally {
        setLoading(false);
      }
    },
    [email]
  );

  const handleResendOTP = useCallback(async () => {
    if (resendDisabled || loading) return;

    setLoading(true);
    setError('');
    setOtp(EMPTY_OTP);

    try {
      await axios.post(`${API_BASE_URL}/auth/password-reset/request`, { email });
      setResendDisabled(true);
      setCountdown(120);
    } catch (resendError: unknown) {
      const message =
        typeof resendError === 'object' && resendError && 'response' in resendError
          ? (resendError as any).response?.data?.detail
          : undefined;
      setError(message || 'Unable to resend the code right now. Try again shortly.');
    } finally {
      setLoading(false);
    }
  }, [email, loading, resendDisabled]);

  const handleResetPassword = useCallback(
    async (event: React.FormEvent) => {
      event.preventDefault();

      if (password !== confirmPassword) {
        setError('Passwords do not match.');
        return;
      }

      if (password.length < 8) {
        setError('Password must be at least 8 characters long.');
        return;
      }

      setLoading(true);
      setError('');

      try {
        await axios.post(`${API_BASE_URL}/auth/password-reset/confirm`, {
          email,
          otp_code: normalizedOtp,
          new_password: password,
        });
        setStep('success');
      } catch (resetError: unknown) {
        const message =
          typeof resetError === 'object' && resetError && 'response' in resetError
            ? (resetError as any).response?.data?.detail
            : undefined;
        setError(message || 'Failed to reset password. Please try again.');
      } finally {
        setLoading(false);
      }
    },
  [confirmPassword, email, normalizedOtp, otp, password]
  );

  const renderError = (message: string) => (
    <div className="flex items-start gap-3 rounded-2xl border border-rose-200/60 bg-rose-50/70 px-4 py-3 text-sm text-rose-600 dark:border-rose-500/40 dark:bg-rose-500/10 dark:text-rose-200">
      <AlertCircle className="h-4 w-4" />
      <span>{message}</span>
    </div>
  );

  const renderStepContent = () => {
    switch (step) {
      case 'email':
        return (
          <form className="space-y-6" onSubmit={handleRequestOTP}>
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-semibold text-gray-700 dark:text-slate-200">
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  placeholder="you@studio.co"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className={`${inputClasses} pl-11`}
                  disabled={loading}
                />
              </div>
            </div>

            {error && renderError(error)}

            <Button type="submit" size="lg" fullWidth isLoading={loading} leadingIcon={<KeyRound className="h-4 w-4" />}>
              {loading ? 'Sending code…' : 'Email me the reset code'}
            </Button>

            <p className="text-xs text-gray-500 dark:text-slate-400">
              We only send reset codes to verified accounts. Need help? Reach us at tryreverseai@gmail.com
            </p>
          </form>
        );
      case 'otp':
        return (
          <div className="space-y-6">
            <div className="space-y-3 text-sm text-gray-600 dark:text-slate-300">
              <p className="font-semibold text-gray-800 dark:text-slate-100">Enter the 6-digit code we emailed to</p>
              <p className="rounded-2xl border border-blue-200/60 bg-blue-50/80 px-4 py-2 text-sm font-semibold text-blue-600 dark:border-indigo-500/30 dark:bg-indigo-500/10 dark:text-indigo-200">
                {email}
              </p>
            </div>

            <OTPInput length={OTP_LENGTH} value={otp} onChange={setOtp} disabled={loading} error={Boolean(error)} />

            {error && renderError(error)}

            {loading && (
              <div className="flex items-center justify-center gap-2 text-sm font-semibold text-indigo-600 dark:text-indigo-300">
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Verifying…</span>
              </div>
            )}

            <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-gray-500 dark:text-slate-400">
              <span>Didn’t get the code?</span>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => void handleResendOTP()}
                disabled={loading || resendDisabled}
                className="rounded-full"
                trailingIcon={<RefreshCw className="h-4 w-4" />}
              >
                {resendDisabled ? `Resend in ${countdown}s` : 'Resend code'}
              </Button>
            </div>

            <Button
              type="button"
              variant="outline"
              size="sm"
              className="rounded-full"
              onClick={() => {
                setStep('email');
                setOtp(EMPTY_OTP);
                setError('');
              }}
              leadingIcon={<ArrowLeft className="h-4 w-4" />}
            >
              Use a different email
            </Button>
          </div>
        );
      case 'password':
        return (
          <form className="space-y-6" onSubmit={handleResetPassword}>
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-semibold text-gray-700 dark:text-slate-200">
                New password
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <input
                  id="password"
                  type={showNewPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  minLength={8}
                  required
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Create a strong password"
                  className={`${inputClasses} pl-11 pr-12`}
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword((prev) => !prev)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-2 text-gray-400 transition hover:text-gray-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-300 dark:text-slate-500 dark:hover:text-slate-300"
                  aria-label={showNewPassword ? 'Hide password' : 'Show password'}
                  aria-pressed={showNewPassword}
                >
                  {showNewPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="confirm-password" className="text-sm font-semibold text-gray-700 dark:text-slate-200">
                Confirm password
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <input
                  id="confirm-password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  minLength={8}
                  required
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  placeholder="Repeat the password"
                  className={`${inputClasses} pl-11 pr-12`}
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword((prev) => !prev)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-2 text-gray-400 transition hover:text-gray-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-300 dark:text-slate-500 dark:hover:text-slate-300"
                  aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                  aria-pressed={showConfirmPassword}
                >
                  {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <div className="rounded-2xl border border-blue-200/60 bg-blue-50/70 p-4 text-xs text-blue-700 dark:border-indigo-500/30 dark:bg-indigo-500/10 dark:text-indigo-200">
              <p className="text-sm font-semibold text-blue-900 dark:text-indigo-100">Security checklist</p>
              <ul className="mt-2 space-y-1">
                <li className={password.length >= 8 ? 'font-semibold text-emerald-600 dark:text-emerald-300' : ''}>
                  • At least 8 characters
                </li>
                <li className={/[A-Z]/.test(password) && /[a-z]/.test(password) ? 'font-semibold text-emerald-600 dark:text-emerald-300' : ''}>
                  • Include upper & lower case letters
                </li>
                <li className={/[0-9]/.test(password) ? 'font-semibold text-emerald-600 dark:text-emerald-300' : ''}>
                  • Add at least one number
                </li>
              </ul>
            </div>

            {error && renderError(error)}

            <Button type="submit" size="lg" fullWidth isLoading={loading} leadingIcon={<Lock className="h-4 w-4" />}>
              {loading ? 'Saving new password…' : 'Reset password'}
            </Button>
          </form>
        );
      case 'success':
        return (
          <div className="flex flex-col items-center gap-5 text-center">
            <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-emerald-500/10 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-300">
              <CheckCircle className="h-10 w-10" />
            </div>
            <div className="space-y-2">
              <h3 className="text-2xl font-semibold text-gray-900 dark:text-slate-100">Password reset successful</h3>
              <p className="text-sm text-gray-600 dark:text-slate-300">
                Your credentials are updated. You can now sign in with your new password.
              </p>
            </div>
            <Button size="md" onClick={() => navigate('/login')}>
              Return to login
            </Button>
          </div>
        );
    }
  };

  return (
    <PageContainer>
      <PageHeader
        title="Reset your password"
        subtitle="Securely recover access to your Prompt Detective workspace with our guided, multi-step flow."
        breadcrumbs={[{ label: 'Account', href: '/login' }, { label: 'Forgot password' }]}
        primaryAction={{ label: 'Back to sign in', onClick: () => navigate('/login') }}
        secondaryAction={{ label: 'Need support?', onClick: () => navigate('/help') }}
        illustration={<Sparkles className="h-12 w-12 text-indigo-500" />}
      />

      <div className="grid gap-6 xl:grid-cols-[1.05fr,0.95fr]">
        <PageSection
          title="How we protect your account"
          description="We combine email verification, timed OTPs, and strength validation to keep your prompts safe."
          icon={<ShieldCheck className="h-6 w-6" />} 
          variant="translucent"
        >
          <div className="grid gap-4 md:grid-cols-2">
            {insights.map((item) => (
              <Card key={item.label} variant="outline" padding="md" className="flex h-full flex-col gap-3 bg-white/85 dark:bg-slate-900/70">
                <Chip tone={item.tone} size="sm">{item.label}</Chip>
                <p className="text-base font-semibold text-gray-900 dark:text-slate-100">{item.description}</p>
                <span className="text-xs uppercase tracking-wide text-gray-400 dark:text-slate-500">Enterprise-ready defaults</span>
              </Card>
            ))}
          </div>

          <div className="mt-6 grid gap-3 text-sm text-gray-500 dark:text-slate-400 sm:grid-cols-2">
            <div className="flex items-center gap-3 rounded-2xl border border-gray-200/60 bg-white/80 px-4 py-3 dark:border-slate-700/60 dark:bg-slate-900/70">
              <Clock className="h-4 w-4 text-blue-500" />
              <span>Codes expire after 2 minutes to prevent unauthorised reuse.</span>
            </div>
            <div className="flex items-center gap-3 rounded-2xl border border-gray-200/60 bg-white/80 px-4 py-3 dark:border-slate-700/60 dark:bg-slate-900/70">
              <Sparkles className="h-4 w-4 text-purple-500" />
              <span>AI-assisted heuristics flag suspicious reset attempts instantly.</span>
            </div>
          </div>

          <div className="mt-6 space-y-4 rounded-3xl border border-white/60 bg-white/70 p-6 shadow-[0_18px_45px_-25px_rgba(59,130,246,0.45)] dark:border-white/5 dark:bg-slate-900/70 dark:shadow-[0_18px_50px_-25px_rgba(15,23,42,0.65)]">
            <Chip tone="gray" size="sm">Progress</Chip>
            <div className="space-y-4">
              {timeline.map((item) => {
                const isActive = item.id === step;
                const isComplete = timeline.indexOf(item) < timeline.findIndex((entry) => entry.id === step);

                return (
                  <div key={item.id} className="flex items-center gap-4">
                    <div
                      className={`flex h-10 w-10 items-center justify-center rounded-full border text-sm font-semibold transition ${
                        isActive
                          ? 'border-blue-500 bg-blue-500/10 text-blue-600 dark:border-indigo-400 dark:bg-indigo-500/10 dark:text-indigo-200'
                          : isComplete
                          ? 'border-emerald-400 bg-emerald-500/10 text-emerald-500 dark:border-emerald-400/60 dark:bg-emerald-500/10 dark:text-emerald-200'
                          : 'border-gray-200 text-gray-400 dark:border-slate-700 dark:text-slate-500'
                      }`}
                    >
                      {timeline.indexOf(item) + 1}
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm font-semibold text-gray-900 dark:text-slate-100">{item.title}</p>
                      <p className="text-xs text-gray-500 dark:text-slate-400">{item.meta}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </PageSection>

        <PageSection
          title={
            step === 'email'
              ? 'Confirm your account'
              : step === 'otp'
              ? 'Verify the reset code'
              : step === 'password'
              ? 'Choose a new password'
              : 'All set!'
          }
          description={
            step === 'email'
              ? 'We will email a one-time password to make sure this account belongs to you.'
              : step === 'otp'
              ? 'Keep this window open while you grab the code from your inbox or spam folder.'
              : step === 'password'
              ? 'A strong password keeps your prompt history and credits safe.'
              : 'Redirecting you back to the login screen.'
          }
          icon={<KeyRound className="h-6 w-6" />}
        >
          <Card variant="elevated" padding="lg" className="space-y-6 bg-white/90 dark:bg-slate-900/85">
            {renderStepContent()}

            {step !== 'success' && (
              <div className="rounded-2xl border border-gray-200/70 bg-white/60 p-4 text-xs text-gray-500 dark:border-slate-700/60 dark:bg-slate-900/70 dark:text-slate-300">
                <p className="text-sm font-semibold text-gray-800 dark:text-slate-100">Need a hand?</p>
                <p className="mt-1">
                  Reach out to our support team at
                  <a
                    href="mailto:tryreverseai@gmail.com"
                    className="ml-1 font-semibold text-blue-600 hover:text-blue-500 dark:text-indigo-300 dark:hover:text-indigo-200"
                  >
                    tryreverseai@gmail.com
                  </a>
                  and we will sort things out in under 12 hours.
                </p>
              </div>
            )}

            {step !== 'success' && (
              <div className="text-center text-sm text-gray-500 dark:text-slate-400">
                <Link to="/login" className="inline-flex items-center gap-2 font-semibold text-blue-600 transition hover:text-blue-500 dark:text-indigo-300 dark:hover:text-indigo-200">
                  <ArrowLeft className="h-4 w-4" /> Back to login
                </Link>
              </div>
            )}
          </Card>
        </PageSection>
      </div>
    </PageContainer>
  );
};

export default ForgotPasswordPage;
