import React, { useCallback, useState } from 'react';
import clsx from 'clsx';
import { useNavigate } from 'react-router-dom';
import { Check, Star, Zap, Shield, Crown, Users, Sparkles, TrendingUp, Clock, Loader2, ArrowRight } from 'lucide-react';
import { RazorpayCheckout, CreditPackCheckout, PaymentMethodsInfo } from '../components/payment/RazorpayCheckout';
import { api } from '../services/api';
import { startTrial } from '../services/trialService';
import { useAuthStore } from '../stores/authStore';
import toast from 'react-hot-toast';

interface PricingPlan {
  id: string;
  name: string;
  priceMonthly: number;
  priceYearly: number;
  dailyLimit: number;
  description: string;
  features: string[];
  cta: string;
  popular: boolean;
  icon: React.ReactNode;
  color: string;
  gradient: string;
}

interface CreditPack {
  name: string;
  price: number;
  analyses: number;
  validity: number;
  perAnalysis: number;
}

const PricingPage: React.FC = () => {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const setUser = useAuthStore((state) => state.setUser);
  const [selectedPlan, setSelectedPlan] = useState<string | null>('pro');
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [showPlanModal, setShowPlanModal] = useState(false);
  const [selectedPlanForPayment, setSelectedPlanForPayment] = useState<PricingPlan | null>(null);
  const [isStartingTrial, setIsStartingTrial] = useState(false);
  const hasUsedTrial = Boolean(user?.has_used_trial);
  const isOnTrial = Boolean(user?.is_on_trial);
  const trialEndsDisplay = user?.trial_ends_at
    ? new Date(user.trial_ends_at).toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short'
      })
    : null;

  const refreshUser = useCallback(async () => {
    try {
      const response = await api.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      console.error('Failed to refresh user profile after subscription change:', error);
    }
  }, [setUser]);

  const handlePaymentSuccess = async (response: any) => {
    console.log('Payment success:', response);
    toast.success('Welcome to premium! Redirecting to dashboard...');
    await refreshUser();
    setTimeout(() => {
      navigate('/dashboard');
    }, 2000);
  };

  const handlePaymentFailure = (error: any) => {
    console.error('Payment failed:', error);
  };

  const handleCreditPackSuccess = (response: any) => {
    console.log('Credit pack purchase success:', response);
    toast.success('Credit pack activated! Redirecting to dashboard...');
    setTimeout(() => {
      navigate('/dashboard');
    }, 2000);
  };

  const handleStartTrial = async () => {
    if (!selectedPlanForPayment) {
      return;
    }

    if (isOnTrial) {
      toast.error('You are already on an active trial. Enjoy exploring premium features!');
      return;
    }

    if (hasUsedTrial) {
      toast.error('You have already used your free trial. Please choose a plan to subscribe.');
      return;
    }

    setIsStartingTrial(true);

    try {
      const response = await startTrial(selectedPlanForPayment.id);
      toast.success(response.message || `Your ${selectedPlanForPayment.name} trial has started!`);
      await refreshUser();
      setShowPlanModal(false);
      navigate('/dashboard');
    } catch (error: any) {
      console.error('Trial start failed:', error);
      const errorMessage = error?.response?.data?.detail || error.message || 'Failed to start trial. Please try again later.';
      toast.error(errorMessage);
    } finally {
      setIsStartingTrial(false);
    }
  };

  const plans: PricingPlan[] = [
    {
      id: 'free',
      name: 'Free',
      priceMonthly: 0,
      priceYearly: 0,
      dailyLimit: 5,
      description: 'Perfect for trying out our service',
      features: [
        '5 analyses per day (resets daily)',
        'Image-to-prompt only',
        'Standard processing (30-60 seconds)',
        'Basic prompt output',
        'Community forum access',
        'Watermarked results',
        'Max file size: 5MB',
        'Email support'
      ],
      cta: 'Get Started Free',
      popular: false,
      icon: <Star className="w-6 h-6" />,
      color: 'gray',
      gradient: 'from-gray-500 to-gray-600'
    },
    {
      id: 'starter',
      name: 'Starter',
      priceMonthly: 299,
      priceYearly: 2990,
      dailyLimit: 15,
      description: 'Individual creators & YouTubers',
      features: [
        '15 analyses per day (resets daily)',
        'Image & video support (videos up to 30 seconds)',
        'Priority processing (15-30 seconds)',
        'Enhanced prompt details (style, lighting, mood)',
        'Download as TXT/JSON',
        'Email support (48-hour response)',
        'No watermark',
        'Max file size: 20MB'
      ],
      cta: 'Start Free Trial',
      popular: false,
      icon: <Zap className="w-6 h-6" />,
      color: 'blue',
      gradient: 'from-blue-500 to-blue-600',
    },
    {
      id: 'pro',
      name: 'Pro',
      priceMonthly: 699,
      priceYearly: 6990,
      dailyLimit: 50,
      description: 'Freelancers, developers & power users',
      features: [
        '50 analyses per day (resets daily)',
        'All video lengths supported (up to 5 minutes)',
        'Fastest processing (10-20 seconds)',
        'Advanced prompt breakdown + model suggestions',
        'REST API access (5,000 calls/month)',
        'Batch processing (upload 10 images at once)',
        'Download as TXT/JSON/CSV',
        'Custom prompt templates',
        'Usage analytics dashboard',
        'Priority email support (24-hour response)',
        'Max file size: 100MB',
        'Webhook notifications'
      ],
      cta: 'Start Free Trial',
      popular: true,
      icon: <Shield className="w-6 h-6" />,
      color: 'purple',
      gradient: 'from-purple-500 to-purple-600',
    },
    {
      id: 'business',
      name: 'Business',
      priceMonthly: 1299,
      priceYearly: 12990,
      dailyLimit: 150,
      description: 'Small agencies, content teams & startups',
      features: [
        '150 analyses per day (resets daily)',
        'Unlimited video length',
        'Ultra-fast processing (5-15 seconds)',
        'Everything in Pro +',
        'API access (20,000 calls/month)',
        'Batch processing (50 images/videos at once)',
        'Team workspace (5 user seats)',
        'Shared prompt library',
        'Advanced analytics & reporting',
        'Priority support (12-hour response)',
        'Custom integrations support',
        'Max file size: 500MB',
        'Rate limit customization'
      ],
      cta: 'Start Free Trial',
      popular: false,
      icon: <Crown className="w-6 h-6" />,
      color: 'amber',
      gradient: 'from-amber-500 to-orange-600',
    }
  ];

  const creditPacks: CreditPack[] = [
    { name: 'Mini', price: 99, analyses: 20, validity: 15, perAnalysis: 4.95 },
    { name: 'Standard', price: 249, analyses: 60, validity: 30, perAnalysis: 4.15 },
    { name: 'Power', price: 499, analyses: 150, validity: 60, perAnalysis: 3.33 }
  ];

  const comparisonData = [
    {
      feature: 'Daily analyses limit',
      free: '5/day',
      pro: '50/day',
      enterprise: '150/day',
      credits: '20-150 flex'
    },
    {
      feature: 'Video support',
      free: 'Images only',
      pro: 'Up to 5 min video',
      enterprise: 'Unlimited length',
      credits: 'All formats'
    },
    {
      feature: 'Processing speed',
      free: 'Standard (30-60s)',
      pro: 'Fast (10-20s)',
      enterprise: 'Ultra-fast (5-15s)',
      credits: 'Priority queue'
    },
    {
      feature: 'Advanced prompt breakdown',
      free: null,
      pro: 'Full breakdown + JSON',
      enterprise: 'Enterprise insights',
      credits: 'Add-on markers'
    },
    {
      feature: 'API access',
      free: null,
      pro: '5,000 calls/mo',
      enterprise: '20,000 calls/mo',
      credits: null
    },
    {
      feature: 'Seats included',
      free: 'Single seat',
      pro: 'Solo + collaborators',
      enterprise: '5 seats (expandable)',
      credits: 'Single seat'
    }
  ];

  const handlePlanSelect = (planId: string) => {
    setSelectedPlan(planId);
  };

  const handleCTAClick = (plan: PricingPlan) => {
    if (plan.id === 'free') {
      navigate('/signup');
    } else {
      // Check if user is logged in
      if (!user) {
        // Redirect to signup with plan info
        navigate('/signup', { 
          state: { 
            planName: plan.name,
            planId: plan.id,
            fromPricing: true 
          } 
        });
      } else {
        // User is logged in, show payment modal
        setSelectedPlanForPayment(plan);
        setIsStartingTrial(false);
        setShowPlanModal(true);
      }
    }
  };

  const getPrice = (plan: PricingPlan) => {
    if (plan.priceMonthly === 0) return 0;

    return billingCycle === 'monthly' ? plan.priceMonthly : plan.priceYearly;
  };

  const getSavings = (plan: PricingPlan) => {
    if (billingCycle === 'yearly' && plan.priceYearly > 0) {
      const monthlyTotal = plan.priceMonthly * 12;
      const yearlySavings = monthlyTotal - plan.priceYearly;
      const percentage = Math.round((yearlySavings / monthlyTotal) * 100);
      return { amount: yearlySavings, percentage };
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 via-white to-gray-50 py-12 transition-colors duration-300 dark:from-slate-950 dark:via-slate-950/95 dark:to-slate-950">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Hero */}
        <div className="relative mb-14 overflow-hidden rounded-[44px] border border-white/60 bg-gradient-to-br from-white via-blue-50 to-purple-50 p-10 shadow-[0_40px_120px_-60px_rgba(79,70,229,0.45)] transition-colors dark:border-white/10 dark:from-slate-900 dark:via-slate-900/80 dark:to-slate-900">
          <div className="absolute inset-x-14 -top-24 h-48 rounded-full bg-gradient-to-r from-purple-300/40 via-blue-300/40 to-sky-300/40 blur-3xl dark:from-indigo-600/20 dark:via-sky-500/20 dark:to-purple-500/20" />
          <div className="relative flex flex-col items-center gap-6 text-center">
            <div className="mx-auto inline-flex items-center gap-2 rounded-full border border-purple-200 bg-white/80 px-5 py-2 text-sm font-semibold text-purple-700 shadow-sm shadow-purple-200 dark:border-indigo-500/60 dark:bg-indigo-500/15 dark:text-indigo-100">
              <Sparkles className="h-4 w-4" />
              Made for India-first teams
            </div>
            <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl dark:text-white">
              Transparent pricing for India-first creators
            </h1>
            <p className="mx-auto max-w-3xl text-lg text-gray-600 dark:text-white/80">
              Upload unlimited images and videos, extract production-grade prompts, and ship content 4× faster.
              <span className="ml-1 font-semibold text-purple-600 dark:text-indigo-200">Save up to 60% vs US tools.</span>
            </p>
            <div className="flex flex-col items-center gap-3">
              <div className="flex items-center gap-4 rounded-full border border-purple-200 bg-white/80 px-4 py-2 shadow-sm shadow-purple-200 dark:border-indigo-500/40 dark:bg-slate-900/70">
                <span
                  className={clsx(
                    'text-sm font-semibold uppercase tracking-wide',
                    billingCycle === 'monthly' ? 'text-purple-600 dark:text-indigo-300' : 'text-gray-500 dark:text-white/75'
                  )}
                >
                  Monthly
                </span>
                <button
                  type="button"
                  onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
                  aria-label={`Switch to ${billingCycle === 'monthly' ? 'yearly' : 'monthly'} billing`}
                  className="relative h-9 w-16 rounded-full border border-purple-200 bg-white/80 transition-all focus:outline-none focus:ring-4 focus:ring-purple-200 dark:border-indigo-500/40 dark:bg-slate-900/70 dark:focus:ring-indigo-500/40"
                >
                  <span
                    aria-hidden="true"
                    className={clsx(
                      'absolute left-1 top-1 inline-flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 text-[11px] font-semibold uppercase text-white shadow-lg transition-transform',
                      billingCycle === 'yearly' ? 'translate-x-7' : 'translate-x-0'
                    )}
                  >
                    {billingCycle === 'yearly' ? 'yr' : 'mo'}
                  </span>
                </button>
                <span
                  className={clsx(
                    'text-sm font-semibold uppercase tracking-wide',
                    billingCycle === 'yearly' ? 'text-purple-600 dark:text-indigo-300' : 'text-gray-500 dark:text-white/75'
                  )}
                >
                  Yearly
                </span>
              </div>
              <div className="inline-flex items-center gap-2 rounded-full bg-white/80 px-4 py-2 text-sm font-semibold text-purple-700 shadow-sm shadow-purple-200 dark:bg-indigo-500/15 dark:text-indigo-100">
                <TrendingUp className="h-3.5 w-3.5" />
                Save 17% instantly when billed yearly
              </div>
            </div>
          </div>
        </div>

        <div className="mt-24">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Compare Plans &amp; Credit Packs</h2>
            <p className="mt-4 mx-auto max-w-2xl text-lg text-gray-600 dark:text-white/80">
              Choose the perfect plan for your workflow. Credits are flexible and can be used for any analysis.
            </p>
          </div>

          <div className="overflow-x-auto rounded-2xl border border-white/60 bg-white shadow-xl dark:border-slate-800 dark:bg-slate-900/80">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-gradient-to-r from-blue-600 to-purple-600 text-left text-white dark:from-indigo-700 dark:to-purple-600/80">
                  <th className="p-6 text-sm font-semibold">Feature</th>
                  <th className="p-6 text-sm font-semibold">Free</th>
                  <th className="p-6 text-sm font-semibold">Pro</th>
                  <th className="p-6 text-sm font-semibold">Enterprise</th>
                  <th className="p-6 text-sm font-semibold">Credits</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-slate-800">
                {comparisonData.map((item) => (
                  <tr key={item.feature} className="transition-colors hover:bg-purple-50 dark:hover:bg-slate-800/70">
                    <td className="p-6 text-sm font-semibold text-gray-900 dark:text-white">{item.feature}</td>
                    <td className="p-6 text-sm text-gray-600 dark:text-white/80">
                      {item.free || <span className="font-semibold text-red-500">✕</span>}
                    </td>
                    <td className="p-6 text-sm text-gray-600 dark:text-white/80">
                      {item.pro || <span className="font-semibold text-red-500">✕</span>}
                    </td>
                    <td className="p-6 text-sm text-gray-600 dark:text-white/80">
                      {item.enterprise || <span className="font-semibold text-red-500">✕</span>}
                    </td>
                    <td className="p-6 text-sm font-semibold text-purple-600 dark:text-indigo-300">
                      {item.credits || <span className="font-semibold text-red-500">✕</span>}
                    </td>
                  </tr>
                ))}
                <tr className="bg-purple-100 dark:bg-slate-800/80">
                  <td className="p-6 text-sm font-semibold text-purple-700 dark:text-indigo-200">Pricing</td>
                  <td className="p-6 text-sm text-gray-600 dark:text-white/80">₹0</td>
                  <td className="p-6 text-sm font-semibold text-purple-600 dark:text-indigo-300">
                    {billingCycle === 'monthly' ? '₹699/mo' : '₹6,990/yr'}
                  </td>
                  <td className="p-6 text-sm text-gray-600 dark:text-white/80">Talk to us</td>
                  <td className="p-6 text-sm font-semibold text-purple-600 dark:text-indigo-300">From ₹199</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {plans.map((plan) => {
            const price = getPrice(plan);
            const savings = getSavings(plan);
            const isSelected = selectedPlan === plan.id;

            return (
              <div
                key={plan.id}
                onClick={() => handlePlanSelect(plan.id)}
                className={clsx(
                  'group relative flex h-full cursor-pointer flex-col overflow-hidden rounded-3xl border border-white/70 bg-white/85 p-8 text-left shadow-[0_28px_90px_-45px_rgba(79,70,229,0.35)] transition-all duration-500 hover:-translate-y-2 hover:border-purple-200/70 hover:bg-white/95 dark:border-white/10 dark:bg-slate-900/80 dark:shadow-[0_28px_90px_-45px_rgba(15,23,42,0.7)]',
                  isSelected ? 'ring-4 ring-purple-200 shadow-[0_40px_120px_-60px_rgba(79,70,229,0.55)] dark:ring-indigo-500/40' : 'ring-0'
                )}
              >
                <div className={`pointer-events-none absolute inset-0 bg-gradient-to-br opacity-0 transition-opacity duration-500 group-hover:opacity-100 ${plan.gradient}`}></div>
                <div className="relative flex flex-1 flex-col gap-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-4">
                      <span className={`flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br ${plan.gradient} text-white shadow-lg shadow-purple-200/60 dark:shadow-indigo-900/50`}>
                        {plan.icon}
                      </span>
                      <div>
                        <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{plan.name}</h3>
                        <p className="text-sm text-gray-500 dark:text-white/80">{plan.description}</p>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      {plan.popular && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 px-3 py-1 text-[11px] font-semibold uppercase text-white shadow-lg">
                          <Star className="h-3 w-3" />
                          Most loved
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-baseline gap-2 text-gray-900 dark:text-white">
                      <span className="text-4xl font-extrabold">₹{price}</span>
                      <span className="text-sm font-semibold text-gray-500 dark:text-white/80">/{billingCycle === 'monthly' ? 'mo' : 'yr'}</span>
                    </div>

                    {savings && (
                      <div className="flex items-center gap-2 text-sm font-semibold text-emerald-600 dark:text-emerald-300">
                        <Sparkles className="h-4 w-4" />
                        Save ₹{savings.amount} ({savings.percentage}% yearly)
                      </div>
                    )}

                    <div className="flex flex-wrap gap-2 text-xs font-semibold text-blue-600 dark:text-indigo-300">
                      <span className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-3 py-1 dark:bg-indigo-500/20">
                        <Clock className="h-3.5 w-3.5" />
                        {plan.dailyLimit} analyses/day
                      </span>
                      <span className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-3 py-1 dark:bg-indigo-500/20">
                        <Sparkles className="h-3.5 w-3.5" />
                        Full AI breakdown
                      </span>
                    </div>
                  </div>

                  <div className="flex-1">
                    <h4 className="text-xs font-bold uppercase tracking-wide text-gray-400 dark:text-white/75">What's included</h4>
                    <div className="mt-4 grid gap-2 text-sm text-gray-700 dark:text-white/85" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))' }}>
                      {plan.features.map((feature, index) => (
                        <div key={index} className="flex items-start gap-2">
                          <Check className="mt-1 h-4 w-4 flex-shrink-0 text-emerald-500" />
                          <span className="text-xs leading-snug">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={(event) => {
                      event.stopPropagation();
                      handleCTAClick(plan);
                    }}
                    className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-full bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-purple-300/40 transition hover:shadow-purple-400/50 dark:shadow-indigo-900/50"
                  >
                    {plan.cta}
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Credit Packs Section */}
        <div className="mt-20 rounded-2xl border border-white/60 bg-gradient-to-br from-blue-50 to-purple-50 p-8 shadow-[0_36px_110px_-60px_rgba(59,130,246,0.35)] transition-colors dark:border-slate-800 dark:from-slate-900/90 dark:to-slate-900/70 dark:shadow-[0_36px_110px_-60px_rgba(15,23,42,0.85)]">
          <div className="mb-8 text-center">
            <h3 className="mb-3 text-3xl font-bold text-gray-900 dark:text-white">
              Sachet Pricing - Pay As You Go
            </h3>
            <p className="text-lg text-gray-600 dark:text-white/80">
              No subscription? No problem. Buy credits that work for you.
            </p>
          </div>

          <div className="mx-auto grid max-w-5xl gap-6 md:grid-cols-3">
            {creditPacks.map((pack) => (
              <div
                key={pack.name}
                className="rounded-xl border-2 border-transparent bg-white p-6 text-gray-800 shadow-md transition-shadow hover:border-blue-300 hover:shadow-xl dark:bg-slate-900/85 dark:text-white dark:hover:border-indigo-500/40"
              >
                <div className="text-center">
                  <h4 className="mb-2 text-xl font-bold text-gray-900 dark:text-white">{pack.name}</h4>
                  <div className="mb-4">
                    <span className="text-3xl font-extrabold text-gray-900 dark:text-white">₹{pack.price}</span>
                  </div>
                  <div className="mb-4 space-y-2 text-sm text-gray-600 dark:text-white/80">
                    <p className="flex items-center justify-center">
                      <Check className="mr-2 h-4 w-4 text-emerald-500" />
                      {pack.analyses} analyses
                    </p>
                    <p className="flex items-center justify-center">
                      <Check className="mr-2 h-4 w-4 text-emerald-500" />
                      Valid for {pack.validity} days
                    </p>
                    <p className="mt-3 text-xs font-semibold text-purple-600 dark:text-indigo-300">
                      ₹{pack.perAnalysis.toFixed(2)} per analysis
                    </p>
                  </div>
                  {!user ? (
                    <button
                      onClick={() => navigate('/signup', { state: { creditPack: pack.name } })}
                      className="w-full rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-2 font-semibold text-white transition-colors hover:from-blue-700 hover:to-purple-700"
                    >
                      Sign Up to Buy
                    </button>
                  ) : (
                    <CreditPackCheckout
                      packName={pack.name}
                      amount={pack.price}
                      onSuccess={handleCreditPackSuccess}
                      onFailure={handlePaymentFailure}
                    />
                  )}
                </div>
              </div>
            ))}
          </div>

                  <p className="mt-6 text-center text-sm text-gray-600 dark:text-white/75">
            💡 Credits don't expire by day - total count is valid for the entire period!
          </p>
        </div>

        {/* Student Discount Banner */}
        <div className="mt-12 rounded-2xl border border-emerald-200/60 bg-gradient-to-r from-emerald-500 to-teal-600 p-6 text-white shadow-[0_26px_90px_-40px_rgba(16,185,129,0.55)] dark:border-emerald-500/30 dark:from-emerald-500/80 dark:to-teal-600/80">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex-1 min-w-[220px]">
              <h3 className="mb-2 flex items-center text-2xl font-bold">
                <Users className="mr-2 h-6 w-6" />
                Student/Educational Discount
              </h3>
              <p className="text-emerald-50">
                Get 40% off with your .edu email address! Starter: ₹179/mo • Pro: ₹419/mo • Business: ₹779/mo
              </p>
            </div>
            <button
              onClick={() => navigate('/signup', { state: { studentDiscount: true } })}
              className="rounded-xl bg-white px-6 py-3 font-semibold text-emerald-600 transition-colors hover:bg-emerald-50 dark:text-emerald-700"
            >
              Claim Discount
            </button>
          </div>
        </div>

        {/* Comparison with US Tools */}
        <div className="mt-20">
          <h3 className="mb-8 text-center text-3xl font-bold text-gray-900 dark:text-white">
            Why Prompt Detective? Compare & Save
          </h3>
          <div className="overflow-x-auto rounded-2xl border border-white/60 bg-white shadow-xl dark:border-slate-800 dark:bg-slate-900/80">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-gradient-to-r from-purple-100 to-blue-100 text-gray-900 dark:from-indigo-900/70 dark:to-slate-900/60 dark:text-white/85">
                  <th className="px-6 py-4 text-left text-sm font-semibold">Feature</th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-purple-700 dark:text-indigo-200">
                    Prompt Detective
                    <div className="mt-1 text-xs font-normal text-purple-600 dark:text-indigo-200/90">🇮🇳 India Optimized</div>
                  </th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700 dark:text-white/85">ImagePrompt.org</th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700 dark:text-white/85">Flux1.ai</th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700 dark:text-white/85">VideoToPrompt</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-slate-800">
                <tr className="transition-colors hover:bg-purple-50 dark:hover:bg-slate-800/70">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">India Pricing</td>
                  <td className="px-6 py-4 text-center text-sm font-semibold text-emerald-600 dark:text-emerald-300">✅ ₹299 - ₹1,299</td>
                  <td className="px-6 py-4 text-center text-sm text-red-600 dark:text-red-300">❌ $14.99+ (₹1,329+)</td>
                  <td className="px-6 py-4 text-center text-sm text-red-600 dark:text-red-300">❌ USD only</td>
                  <td className="px-6 py-4 text-center text-sm text-red-600 dark:text-red-300">❌ USD only</td>
                </tr>
                <tr className="transition-colors hover:bg-purple-50 dark:hover:bg-slate-800/70">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">Daily Limits</td>
                  <td className="px-6 py-4 text-center text-sm font-semibold text-emerald-600 dark:text-emerald-300">✅ 5-150/day</td>
                  <td className="px-6 py-4 text-center text-sm text-gray-600 dark:text-white/80">❌ Monthly caps</td>
                  <td className="px-6 py-4 text-center text-sm text-gray-600 dark:text-white/80">✅ Unlimited</td>
                  <td className="px-6 py-4 text-center text-sm text-yellow-600 dark:text-amber-300">⚠️ Limited</td>
                </tr>
                <tr className="transition-colors hover:bg-purple-50 dark:hover:bg-slate-800/70">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">Video Support</td>
                  <td className="px-6 py-4 text-center text-sm font-semibold text-emerald-600 dark:text-emerald-300">✅ All tiers</td>
                  <td className="px-6 py-4 text-center text-sm text-gray-600 dark:text-white/80">❌ Pro only</td>
                  <td className="px-6 py-4 text-center text-sm text-red-600 dark:text-red-300">❌ None</td>
                  <td className="px-6 py-4 text-center text-sm text-yellow-600 dark:text-amber-300">✅ Limited</td>
                </tr>
                <tr className="transition-colors hover:bg-purple-50 dark:hover:bg-slate-800/70">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">API Access</td>
                  <td className="px-6 py-4 text-center text-sm font-semibold text-emerald-600 dark:text-emerald-300">✅ At ₹699</td>
                  <td className="px-6 py-4 text-center text-sm text-gray-600 dark:text-white/80">❌ Higher tiers</td>
                  <td className="px-6 py-4 text-center text-sm text-red-600 dark:text-red-300">❌ None</td>
                  <td className="px-6 py-4 text-center text-sm text-red-600 dark:text-red-300">❌ None</td>
                </tr>
                <tr className="transition-colors hover:bg-purple-50 dark:hover:bg-slate-800/70">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">Sachet Pricing</td>
                  <td className="px-6 py-4 text-center text-sm font-semibold text-emerald-600 dark:text-emerald-300">✅ ₹99-₹499</td>
                  <td className="px-6 py-4 text-center text-sm text-red-600 dark:text-red-300">❌ No</td>
                  <td className="px-6 py-4 text-center text-sm text-red-600 dark:text-red-300">❌ No</td>
                  <td className="px-6 py-4 text-center text-sm text-red-600 dark:text-red-300">❌ No</td>
                </tr>
                <tr className="bg-purple-100 transition-colors hover:bg-purple-200/70 dark:bg-slate-800/80 dark:hover:bg-slate-800/70">
                  <td className="px-6 py-4 text-sm font-bold text-gray-900 dark:text-white">Your Savings</td>
                  <td className="px-6 py-4 text-center text-lg font-bold text-green-700 dark:text-emerald-300">Save 40-60%</td>
                  <td className="px-6 py-4 text-center text-sm text-gray-400 dark:text-white/65">-</td>
                  <td className="px-6 py-4 text-center text-sm text-gray-400 dark:text-white/65">-</td>
                  <td className="px-6 py-4 text-center text-sm text-gray-400 dark:text-white/65">-</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Social Proof */}
        <div className="mt-16 text-center">
          <div className="inline-flex items-center rounded-full bg-gradient-to-r from-purple-100 to-blue-100 px-6 py-3 shadow-sm dark:from-indigo-900/60 dark:to-blue-900/60">
            <Users className="mr-2 h-5 w-5 text-purple-600 dark:text-indigo-300" />
            <span className="font-semibold text-purple-900 dark:text-indigo-100">
              Join 2,000+ Indian creators already using Prompt Detective
            </span>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mt-20">
          <h3 className="mb-12 text-center text-3xl font-bold text-gray-900 dark:text-white">
            Frequently Asked Questions
          </h3>
          <div className="mx-auto max-w-3xl">
            <div className="space-y-6">
              {[
                {
                  question: 'How does the daily limit work?',
                  answer: 'Your daily limit resets every day at midnight IST. This means you get fresh analyses every day - it never runs out! Unlike monthly caps that force you to wait 30 days, our daily reset ensures consistent access.'
                },
                {
                  question: 'Can I use UPI/Paytm/Razorpay?',
                  answer: 'Yes! We accept UPI, Paytm, Razorpay, credit/debit cards, and net banking. Payment is 100% secure and processed in INR.'
                },
                {
                  question: 'What if I run out of analyses?',
                  answer: 'You can upgrade your plan anytime, or purchase a credit pack for immediate access. Credit packs are perfect for occasional bursts of work!'
                },
                {
                  question: 'Can I switch plans later?',
                  answer: 'Absolutely! You can upgrade or downgrade any time from your billing settings. Changes take effect immediately and we automatically apply pro-rated charges or credits.'
                },
                {
                  question: 'Do you offer refunds?',
                  answer: 'Absolutely! We offer a 14-day money-back guarantee on all paid plans. If you\'re not satisfied, we\'ll refund you - no questions asked.'
                },
                {
                  question: 'Do you provide GST invoices?',
                  answer: 'Yes. Every purchase comes with a GST-compliant invoice delivered instantly to your email. You can also download past invoices from the dashboard.'
                },
                {
                  question: 'What payment methods do you accept?',
                  answer: 'We accept UPI, Paytm, Razorpay, all major credit/debit cards, and net banking. For Business plans, we can also arrange invoice billing.'
                },
                {
                  question: 'Can I get support in Hindi?',
                  answer: 'Yes! Our email support team can assist you in both English and Hindi during IST business hours (9 AM - 6 PM IST).'
                }
              ].map((faq, index) => (
                <div 
                  key={index}
                  className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md dark:border-slate-800 dark:bg-slate-900/75"
                >
                  <h4 className="mb-3 text-lg font-semibold text-gray-900 dark:text-white">
                    {faq.question}
                  </h4>
                  <p className="leading-relaxed text-gray-600 dark:text-white/80">
                    {faq.answer}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Final CTA */}
        <div className="mt-20 bg-gradient-to-r from-purple-600 via-blue-600 to-purple-600 rounded-2xl shadow-2xl overflow-hidden">
          <div className="px-8 py-12 text-center">
            <h3 className="text-3xl font-bold text-white mb-4">
              Ready to Transform Your Workflow?
            </h3>
            <p className="text-xl text-purple-100 mb-4 max-w-2xl mx-auto">
              Join thousands of Indian creators who've made the switch
            </p>
            <div className="flex items-center justify-center space-x-4 text-sm text-purple-100 mb-8">
              <span className="flex items-center">
                <Check className="w-4 h-4 mr-1" /> 14-day free trial
              </span>
              <span className="flex items-center">
                <Check className="w-4 h-4 mr-1" /> No credit card required
              </span>
              <span className="flex items-center">
                <Check className="w-4 h-4 mr-1" /> Cancel anytime
              </span>
            </div>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => navigate('/signup')}
                className="px-8 py-4 bg-white text-purple-600 rounded-xl font-bold text-lg hover:bg-purple-50 transition-colors shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                Start Free Trial →
              </button>
              <button
                onClick={() => navigate('/signup', { state: { creditPack: 'Mini' } })}
                className="px-8 py-4 bg-purple-500 text-white border-2 border-white rounded-xl font-bold text-lg hover:bg-purple-400 transition-colors shadow-lg"
              >
                Buy Credit Pack
              </button>
            </div>
            <p className="mt-6 text-sm text-purple-200">
              🎉 Start today and cancel anytime—no hidden fees, ever.
            </p>
          </div>
        </div>

        {/* Trust Badges */}
  <div className="mt-16 flex items-center justify-center space-x-8 text-gray-400 dark:text-white/70">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            <span className="text-sm">Secure Payments</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="h-5 w-5" />
            <span className="text-sm">14-Day Guarantee</span>
          </div>
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            <span className="text-sm">2000+ Users</span>
          </div>
        </div>
      </div>

      {/* Plan Action Modal */}
      {showPlanModal && selectedPlanForPayment && (
        <div className="fixed inset-0 z-[120] flex items-center justify-center bg-slate-950/80 px-3 py-6 backdrop-blur">
          <div className="relative flex w-full max-w-4xl flex-col overflow-hidden rounded-3xl border border-white/10 bg-white/10 shadow-[0_50px_140px_-60px_rgba(79,70,229,0.6)] backdrop-blur-xl dark:bg-slate-900/90">
            <button
              onClick={() => setShowPlanModal(false)}
              className="absolute right-4 top-4 z-10 rounded-full bg-white/10 p-2 text-white transition hover:bg-white/20"
              aria-label="Close"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div className="max-h-[85vh] overflow-y-auto p-6 sm:p-8">
              <div className="grid gap-6 lg:grid-cols-[1.15fr,0.85fr]">
                <div className="space-y-6 rounded-3xl border border-white/15 bg-white/15 p-6 text-white shadow-inner shadow-indigo-500/20">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-4">
                      <span className={`flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br ${selectedPlanForPayment.gradient} text-white shadow-lg shadow-purple-500/30`}>
                        {selectedPlanForPayment.icon}
                      </span>
                      <div>
                        <p className="text-sm uppercase tracking-[0.35em] text-white/70">Plan preview</p>
                        <h3 className="mt-2 text-3xl font-semibold text-white">{selectedPlanForPayment.name}</h3>
                        <p className="text-sm text-white/70">{selectedPlanForPayment.description}</p>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-3xl border border-white/20 bg-white/10 p-6">
                    <div className="flex items-baseline gap-2">
                      <span className="text-4xl font-extrabold">₹{getPrice(selectedPlanForPayment)}</span>
                      <span className="text-sm font-semibold text-white/70">/{billingCycle === 'monthly' ? 'mo' : 'yr'}</span>
                    </div>
                    <p className="mt-3 text-sm text-white/70">Switch to yearly to unlock our best pricing.</p>

                    <div className="mt-5 grid gap-3 text-sm text-white/80 sm:grid-cols-2">
                      <div className="flex items-center gap-2">
                        <Check className="h-4 w-4 text-emerald-300" />
                        {selectedPlanForPayment.dailyLimit} analyses/day, resets every midnight IST
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-sky-300" />
                        Priority processing & concierge support
                      </div>
                      <div className="flex items-center gap-2">
                        <Sparkles className="h-4 w-4 text-purple-300" />
                        Advanced prompt breakdown + enhancement markers
                      </div>
                      <div className="flex items-center gap-2">
                        <Zap className="h-4 w-4 text-amber-300" />
                        API + batch workflows included
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3 rounded-3xl border border-white/15 bg-white/5 p-6 text-xs leading-relaxed text-white/70">
                    <p>• UPI, credit/debit cards, and GST invoices supported via Razorpay.</p>
                    <p>• You can upgrade, downgrade, or cancel anytime. No long-term lock-ins.</p>
                    <p>• Questions? Write to <span className="font-semibold text-white">tryreverseai@gmail.com</span>.</p>
                  </div>
                </div>

                <div className="flex flex-col gap-4">
                  <div className="rounded-3xl border border-emerald-200/60 bg-white/80 p-6 text-slate-800 shadow-[0_24px_70px_-40px_rgba(16,185,129,0.55)] dark:border-emerald-500/30 dark:bg-slate-900/80 dark:text-white/85">
                  <h4 className="flex items-center gap-2 text-lg font-semibold">
                    <Sparkles className="h-5 w-5 text-emerald-500" />
                    Start 3-day trial
                  </h4>
                  <p className="mt-2 text-sm text-slate-600 dark:text-white/75">
                    Unlock full access instantly. Downgrades automatically after the trial — no auto-charge.
                  </p>
                  <button
                    onClick={handleStartTrial}
                    disabled={isStartingTrial || hasUsedTrial || isOnTrial}
                    className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-full bg-gradient-to-r from-emerald-500 via-emerald-600 to-teal-600 px-6 py-3 text-sm font-semibold text-white shadow-lg transition hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {isStartingTrial ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Starting trial…
                      </>
                    ) : (
                      'Start free trial'
                    )}
                  </button>
                  {hasUsedTrial && !isOnTrial && (
                    <p className="mt-3 rounded-2xl border border-red-200 bg-red-50 px-3 py-2 text-xs font-medium text-red-500 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-200">
                      You have already used your free trial on this account.
                    </p>
                  )}
                  {isOnTrial && trialEndsDisplay && (
                    <p className="mt-3 rounded-2xl border border-blue-200 bg-blue-50 px-3 py-2 text-xs font-medium text-blue-600 dark:border-blue-500/30 dark:bg-blue-500/10 dark:text-blue-200">
                      Trial active until {trialEndsDisplay}.
                    </p>
                  )}
                  </div>

                  <div className="rounded-3xl border border-white/20 bg-white/80 p-6 text-slate-800 shadow-[0_24px_70px_-40px_rgba(79,70,229,0.55)] dark:border-white/10 dark:bg-slate-900/80 dark:text-white/85">
                  <h4 className="flex items-center gap-2 text-lg font-semibold">
                    <Shield className="h-5 w-5 text-purple-500" />
                    Buy now
                  </h4>
                  <p className="mt-2 text-sm text-slate-600 dark:text-white/75">
                    Secure checkout with instant GST invoices and UPI support.
                  </p>
                  <RazorpayCheckout
                    amount={getPrice(selectedPlanForPayment)}
                    planId={selectedPlanForPayment.id}
                    planName={selectedPlanForPayment.name}
                    billingCycle={billingCycle}
                    onSuccess={handlePaymentSuccess}
                    onFailure={handlePaymentFailure}
                    buttonText={`Pay ₹${getPrice(selectedPlanForPayment)} securely`}
                    buttonClassName="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-full bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-lg transition hover:shadow-xl"
                  />
                    <div className="mt-4 rounded-2xl border border-white/40 bg-white/60 p-4 text-xs text-slate-600 dark:border-white/10 dark:bg-slate-900/70 dark:text-white/80">
                      <PaymentMethodsInfo />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PricingPage;
