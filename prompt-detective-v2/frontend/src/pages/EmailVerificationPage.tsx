import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AlertCircle, ArrowLeft, CheckCircle, Clock, Mail, RefreshCw, ShieldCheck, Sparkles } from 'lucide-react';
import axios from 'axios';
import PageContainer from '../components/page/PageContainer';
import PageHeader from '../components/PageHeader';
import PageSection from '../components/page/PageSection';
import Card from '../components/ui/Card';
import Chip from '../components/ui/Chip';
import { Button } from '../components/ui/Button';
import OTPInput from '../components/OTPInput';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const EmailVerificationPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const email: string = location.state?.email ?? '';

  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [resendDisabled, setResendDisabled] = useState(false);
  const [countdown, setCountdown] = useState(0);

  const verificationBenefits = useMemo(
    () => [
      {
        label: 'Secure-first onboarding',
        tone: 'emerald' as const,
        description: 'Two-step verification locks your workspace to trusted collaborators only.',
      },
      {
        label: 'Global delivery network',
        tone: 'blue' as const,
        description: 'Codes arrive within seconds via redundant email pathways, even during peak hours.',
      },
      {
        label: 'Priority support',
        tone: 'purple' as const,
        description: 'Need help? Our concierge team responds in under 10 minutes during IST business hours.',
      },
    ],
    []
  );

  const requestVerificationCode = useCallback(async () => {
    if (!email) return;
    setLoading(true);
    setError('');
    setOtp('');

    try {
      await axios.post(`${API_BASE_URL}/auth/email-verification/request`, { email });
      setResendDisabled(true);
      setCountdown(120);
    } catch (requestError: unknown) {
      const message =
        typeof requestError === 'object' && requestError && 'response' in requestError
          ? (requestError as any).response?.data?.detail
          : undefined;
      setError(message || 'Failed to send verification code. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [email]);

  const handleVerifyOtp = useCallback(async () => {
    if (otp.length !== 6) {
      setError('Please enter the 6-digit code we emailed you.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/auth/email-verification/verify`, {
        email,
        otp_code: otp,
      });

      if (response.data?.message) {
        setSuccess(true);
        setTimeout(() => {
          navigate('/dashboard', {
            state: { message: 'Email verified successfully! Welcome to Prompt Detective 🎉' },
          });
        }, 2200);
      }
    } catch (verificationError: unknown) {
      const message =
        typeof verificationError === 'object' && verificationError && 'response' in verificationError
          ? (verificationError as any).response?.data?.detail
          : undefined;
      setError(message || 'Invalid code. Please try again.');
      setOtp('');
    } finally {
      setLoading(false);
    }
  }, [email, navigate, otp]);

  useEffect(() => {
    if (!email) {
      navigate('/login');
      return;
    }
    void requestVerificationCode();
  }, [email, navigate, requestVerificationCode]);

  useEffect(() => {
    if (!resendDisabled) return;
    if (countdown <= 0) {
      setResendDisabled(false);
      return;
    }
    const timer = setTimeout(() => setCountdown((value) => value - 1), 1000);
    return () => clearTimeout(timer);
  }, [countdown, resendDisabled]);

  useEffect(() => {
    if (otp.length === 6 && !loading && !success) {
      void handleVerifyOtp();
    }
  }, [otp, loading, success, handleVerifyOtp]);

  const handleResend = () => {
    if (loading || resendDisabled) return;
    void requestVerificationCode();
  };

  if (success) {
    return (
      <PageContainer>
        <PageHeader
          title="Email verified"
          subtitle="Your workspace is now secured. We’re redirecting you to the dashboard."
          breadcrumbs={[{ label: 'Account', href: '/signup' }, { label: 'Verification' }]}
          illustration={<CheckCircle className="h-12 w-12 text-emerald-500" />}
        />
        <PageSection icon={<Sparkles className="h-6 w-6" />} title="You’re all set" variant="translucent">
          <Card variant="elevated" padding="lg" className="flex flex-col items-center gap-4 text-center">
            <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-emerald-500/10 text-emerald-500 dark:bg-emerald-400/10 dark:text-emerald-300">
              <CheckCircle className="h-10 w-10" />
            </div>
            <p className="text-xl font-semibold text-gray-900 dark:text-slate-100">Email confirmed</p>
            <p className="max-w-md text-sm text-gray-500 dark:text-slate-400">
              Your login is secure and analytics syncing is unlocked. Sit tight while we take you to the dashboard.
            </p>
            <div className="flex items-center gap-2 rounded-full border border-emerald-200/60 bg-emerald-50/80 px-4 py-2 text-xs font-semibold text-emerald-600 dark:border-emerald-400/30 dark:bg-emerald-500/10 dark:text-emerald-200">
              <Clock className="h-3.5 w-3.5" /> Redirecting…
            </div>
          </Card>
        </PageSection>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageHeader
        title="Verify your email"
        subtitle="We just sent a six-digit code. Enter it below to activate your Prompt Detective workspace."
        breadcrumbs={[{ label: 'Account', href: '/signup' }, { label: 'Verification' }]}
        primaryAction={{ label: 'Need a new email?', onClick: () => navigate('/signup') }}
        secondaryAction={{ label: 'Back to login', onClick: () => navigate('/login') }}
        illustration={<Mail className="h-12 w-12 text-indigo-500" />}
      />

      <div className="grid gap-6 xl:grid-cols-[1.05fr,0.95fr]">
        <PageSection
          title="Powering secure insights"
          description="Verification routes requests through redundant providers and rate limits the experience to keep your data safe."
          icon={<ShieldCheck className="h-6 w-6" />}
          variant="translucent"
        >
          <div className="grid gap-4 md:grid-cols-2">
            {verificationBenefits.map((item) => (
              <Card key={item.label} variant="outline" padding="md" className="flex h-full flex-col gap-3 bg-white/85 dark:bg-slate-900/70">
                <Chip tone={item.tone} size="sm">{item.label}</Chip>
                <p className="text-base font-semibold text-gray-900 dark:text-slate-100">{item.description}</p>
                <span className="text-xs uppercase tracking-wide text-gray-400 dark:text-slate-500">Enterprise-grade defaults</span>
              </Card>
            ))}
          </div>

          <div className="mt-6 space-y-3 rounded-3xl border border-white/60 bg-white/70 p-6 shadow-[0_18px_45px_-25px_rgba(59,130,246,0.45)] dark:border-white/5 dark:bg-slate-900/70 dark:shadow-[0_18px_50px_-25px_rgba(15,23,42,0.65)]">
            <Chip tone="blue" size="sm">Deliverability tips</Chip>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-slate-300">
              <li>• Add hello@promptdetective.ai to your contacts to whitelist the sender.</li>
              <li>• Check your Promotions or Spam folders if the email doesn’t appear within 30 seconds.</li>
              <li>• Still nothing? Resend the code or reach us at support for a manual activation link.</li>
            </ul>
          </div>
        </PageSection>

        <PageSection
          title="Enter the 6-digit code"
          description={`We sent an authentication code to ${email || 'your email'}.`}
          icon={<Sparkles className="h-6 w-6" />}
        >
          <Card variant="elevated" padding="lg" className="space-y-6 bg-white/90 dark:bg-slate-900/85">
            <div className="space-y-4 text-sm text-gray-600 dark:text-slate-300">
              <p className="font-semibold text-gray-800 dark:text-slate-100">Step 1 · Retrieve the code</p>
              <p>Open the email titled “Prompt Detective Verification” and copy the six digits we sent to you.</p>
            </div>

            <OTPInput length={6} value={otp} onChange={setOtp} disabled={loading} error={Boolean(error)} />

            {error && (
              <div className="flex items-start gap-3 rounded-2xl border border-rose-200/60 bg-rose-50/70 px-4 py-3 text-sm text-rose-600 dark:border-rose-500/40 dark:bg-rose-500/10 dark:text-rose-200">
                <AlertCircle className="h-4 w-4" />
                <span>{error}</span>
              </div>
            )}

            {loading && (
              <div className="flex items-center justify-center gap-2 text-sm font-semibold text-indigo-600 dark:text-indigo-300">
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Processing…</span>
              </div>
            )}

            <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-gray-500 dark:text-slate-400">
              <span>Didn’t receive the code?</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleResend}
                disabled={loading || resendDisabled}
                className="rounded-full"
                trailingIcon={<RefreshCw className="h-4 w-4" />}
              >
                {resendDisabled ? `Resend available in ${countdown}s` : 'Resend code'}
              </Button>
            </div>

            <div className="rounded-2xl border border-gray-200/70 bg-white/60 p-4 text-xs text-gray-500 dark:border-slate-700/60 dark:bg-slate-900/70 dark:text-slate-300">
              <p className="text-sm font-semibold text-gray-800 dark:text-slate-100">Verification window</p>
              <p className="mt-1">Codes expire in 10 minutes. If the timer runs out, request a fresh one above.</p>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs">
              <button
                type="button"
                className="inline-flex items-center gap-2 text-gray-500 transition hover:text-gray-900 dark:text-slate-400 dark:hover:text-slate-100"
                onClick={() => navigate('/signup')}
              >
                <ArrowLeft className="h-3.5 w-3.5" /> Use a different email
              </button>
              <Button size="sm" onClick={handleVerifyOtp} isLoading={loading}>
                Verify and continue
              </Button>
            </div>
          </Card>
        </PageSection>
      </div>
    </PageContainer>
  );
};

export default EmailVerificationPage;
