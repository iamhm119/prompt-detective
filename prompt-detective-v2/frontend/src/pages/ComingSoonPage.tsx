import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft, Rocket, Clock, Mail, CheckCircle, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { subscribeToWaitlist } from '../services/waitlistService';

interface LocationState {
  planName?: string;
  fromPricing?: boolean;
}

const ComingSoonPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState;
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [waitlistMessage, setWaitlistMessage] = useState('');
  const [formError, setFormError] = useState('');

  useEffect(() => {
    // Scroll to top when component mounts
    window.scrollTo(0, 0);
  }, []);

  const handleSubscribe = async (event: React.FormEvent) => {
    event.preventDefault();

    const trimmedEmail = email.trim();
    if (!trimmedEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmedEmail)) {
      setFormError('Enter a valid email to join the waitlist.');
      toast.error('Please add a valid email address.');
      return;
    }

    setIsSubmitting(true);
    setFormError('');

    try {
      const response = await subscribeToWaitlist({
        email: trimmedEmail,
        planName,
        source: state?.fromPricing ? 'pricing-coming-soon' : 'coming-soon-page',
        notes: 'coming-soon-waitlist',
      });

      setSubscribed(true);
      setWaitlistMessage(response.message);
      setEmail('');
      toast.success(response.already_joined ? 'You were already on the waitlist—we’ll keep you posted!' : 'You’re on the waitlist! We’ll email launch details soon.');
    } catch (error: any) {
      const message = error?.response?.data?.detail ?? 'Unable to join the waitlist right now. Please try again shortly.';
      setFormError(message);
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const planName = state?.planName || 'Premium';

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4 dark:from-[#050916] dark:via-[#050916] dark:to-[#0b1022]">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => state?.fromPricing ? navigate('/pricing') : navigate(-1)}
          className="mb-8 flex items-center text-gray-600 hover:text-gray-900 transition-colors group dark:text-white/70 dark:hover:text-white"
        >
          <ArrowLeft className="w-5 h-5 mr-2 transform group-hover:-translate-x-1 transition-transform" />
          Back to {state?.fromPricing ? 'Pricing' : 'Previous Page'}
        </button>

        {/* Main Content */}
  <div className="overflow-hidden rounded-2xl border border-white/70 bg-white shadow-xl dark:border-white/10 dark:bg-slate-900/85">
          {/* Header Section */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-12 text-center">
            <div className="flex justify-center mb-6">
              <div className="bg-white/20 backdrop-blur-sm rounded-full p-6">
                <Rocket className="w-16 h-16 text-white" />
              </div>
            </div>
            <h1 className="text-4xl font-extrabold text-white mb-4">
              {planName} Plan Coming Soon! 🚀
            </h1>
            <p className="text-xl text-blue-100 max-w-2xl mx-auto">
              We're working hard to bring you amazing features. Get notified when we launch!
            </p>
          </div>

          {/* Content Section */}
          <div className="px-8 py-12">
            {/* What's Coming */}
            <div className="mb-12">
              <h2 className="mb-6 flex items-center text-2xl font-bold text-gray-900 dark:text-white">
                <Clock className="mr-3 h-6 w-6 text-blue-600 dark:text-indigo-300" />
                What's Coming in {planName}
              </h2>
              <div className="grid md:grid-cols-2 gap-6">
                {[
                  {
                    title: 'Enhanced Processing',
                    description: 'Lightning-fast analysis with priority queue access'
                  },
                  {
                    title: 'Advanced Features',
                    description: 'API access, batch processing, and custom prompts'
                  },
                  {
                    title: 'Premium Support',
                    description: '24/7 priority support with dedicated account manager'
                  },
                  {
                    title: 'Exclusive Tools',
                    description: 'Early access to beta features and new AI models'
                  }
                ].map((feature, index) => (
                  <div
                    key={index}
                    className="rounded-xl border border-blue-100 bg-gradient-to-br from-blue-50 to-purple-50 p-6 dark:border-indigo-500/20 dark:from-slate-900/80 dark:via-slate-900/70 dark:to-indigo-950/40"
                  >
                    <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 dark:text-white/80">{feature.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Newsletter Subscription */}
            <div className="rounded-xl border border-gray-200 bg-gradient-to-br from-gray-50 to-blue-50 p-8 dark:border-slate-700/70 dark:from-slate-900/85 dark:via-slate-900/75 dark:to-indigo-950/60">
              <div className="text-center mb-6">
                <Mail className="mx-auto mb-4 h-12 w-12 text-blue-600 dark:text-indigo-300" />
                <h3 className="mb-2 text-2xl font-bold text-gray-900 dark:text-white">
                  Be the First to Know
                </h3>
                <p className="text-gray-600 dark:text-white/80">
                  Join our waitlist and get exclusive early bird pricing when we launch
                </p>
              </div>

              {!subscribed ? (
                <form onSubmit={handleSubscribe} className="max-w-md mx-auto">
                  <div className="flex flex-col sm:flex-row gap-3">
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email address"
                      required
                      className="flex-1 rounded-lg border border-gray-300 px-4 py-3 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-600 dark:bg-slate-900/60 dark:text-slate-100 dark:focus:border-blue-400 dark:focus:ring-blue-500/30"
                    />
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
                    >
                      {isSubmitting ? (
                        <span className="flex items-center gap-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Joining…
                        </span>
                      ) : (
                        'Notify Me'
                      )}
                    </button>
                  </div>
                  {formError && (
                    <p className="mt-3 text-sm font-medium text-rose-600 dark:text-rose-300">{formError}</p>
                  )}
                  <p className="mt-3 text-center text-xs text-gray-500 dark:text-white/60">
                    We respect your privacy. Unsubscribe at any time.
                  </p>
                </form>
              ) : (
                <div className="max-w-md mx-auto text-center">
                  <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-6 text-emerald-700 dark:border-emerald-400/40 dark:bg-emerald-500/10 dark:text-emerald-200">
                    <CheckCircle className="mx-auto mb-3 h-12 w-12 text-emerald-500 dark:text-emerald-300" />
                    <h4 className="mb-2 text-lg font-semibold text-emerald-900 dark:text-emerald-100">
                      You're on the list! 🎉
                    </h4>
                    <p className="text-sm dark:text-white/80">
                      {waitlistMessage || `We'll notify you as soon as the ${planName} plan is available.`}
                    </p>
                    <button
                      type="button"
                      onClick={() => {
                        setSubscribed(false);
                        setWaitlistMessage('');
                      }}
                      className="mt-4 inline-flex items-center justify-center rounded-full border border-emerald-400 px-4 py-2 text-sm font-semibold text-emerald-700 transition hover:bg-emerald-500/10 dark:border-emerald-300/40 dark:text-emerald-200 dark:hover:bg-emerald-500/20"
                    >
                      Join with another email
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Timeline */}
            <div className="mt-12">
              <h3 className="mb-6 text-center text-2xl font-bold text-gray-900 dark:text-white">
                Launch Timeline
              </h3>
              <div className="relative">
                <div className="absolute left-1/2 transform -translate-x-1/2 h-full w-1 bg-gradient-to-b from-blue-600 to-purple-600 opacity-20"></div>
                <div className="space-y-8">
                  {[
                    { phase: 'Phase 1', title: 'Beta Testing', status: 'In Progress', date: 'Current' },
                    { phase: 'Phase 2', title: 'Feature Completion', status: 'Next', date: 'Q1 2025' },
                    { phase: 'Phase 3', title: 'Public Launch', status: 'Upcoming', date: 'Q2 2025' }
                  ].map((item, index) => (
                    <div key={index} className="relative flex items-center">
                      <div className="flex-1 pr-8 text-right">
                        <h4 className="font-semibold text-gray-900 dark:text-white">{item.phase}</h4>
                        <p className="text-sm text-gray-600 dark:text-white/80">{item.title}</p>
                      </div>
                      <div className="relative z-10 flex h-12 w-12 items-center justify-center rounded-full border-4 border-white bg-gradient-to-br from-blue-600 to-purple-600 shadow-lg dark:border-slate-900">
                        <span className="text-white font-bold text-sm">{index + 1}</span>
                      </div>
                      <div className="flex-1 pl-8">
                        <p className="text-sm font-medium text-blue-600 dark:text-indigo-300">{item.status}</p>
                        <p className="text-sm text-gray-600 dark:text-white/70">{item.date}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="mt-12 flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => navigate('/pricing')}
                className="rounded-lg bg-blue-600 px-8 py-3 font-semibold text-white transition-colors hover:bg-blue-700"
              >
                View All Plans
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className="rounded-lg border-2 border-blue-600 bg-white px-8 py-3 font-semibold text-blue-600 transition-colors hover:bg-blue-50 dark:border-indigo-400 dark:bg-transparent dark:text-indigo-200 dark:hover:bg-indigo-500/10"
              >
                Go to Dashboard
              </button>
            </div>
          </div>
        </div>

        {/* Additional Info */}
        <div className="mt-8 text-center text-gray-600 dark:text-white/70">
          <p className="text-sm">
            Have questions? <a href="mailto:support@promptdetective.com" className="text-blue-600 hover:underline dark:text-indigo-300 dark:hover:text-indigo-200">Contact our team</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ComingSoonPage;
