import React, { useEffect, useMemo, useState } from 'react';
import toast from 'react-hot-toast';
import { ContactTopic, getContactTopics, submitContactRequest } from '../services/contactService';
import { useAuthStore } from '../stores/authStore';

interface FormState {
  name: string;
  email: string;
  topic: string;
  selectedQuestion?: string | null;
  message?: string;
  accountStage?: string;
  consent: boolean;
}

const ACCOUNT_STAGE_OPTIONS = [
  'Exploring the free tier',
  'On a trial plan',
  'Active subscriber',
  'Evaluating for a team/agency',
  'Enterprise security review',
];

const baseFieldClasses =
  'rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm transition focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-900/70 dark:text-slate-100 dark:focus:border-blue-400 dark:focus:ring-blue-500/30';

const ContactPage: React.FC = () => {
  const { user } = useAuthStore();
  const [topics, setTopics] = useState<ContactTopic[]>([]);
  const [loadingTopics, setLoadingTopics] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const initialForm = useMemo<FormState>(() => ({
    name: user?.full_name || user?.email || '',
    email: user?.email || '',
    topic: '',
    selectedQuestion: undefined,
    message: '',
    accountStage: user?.subscription_tier ? user.subscription_tier : undefined,
    consent: true,
  }), [user]);

  const [form, setForm] = useState<FormState>(initialForm);

  useEffect(() => {
    setForm(initialForm);
  }, [initialForm]);

  useEffect(() => {
    let mounted = true;
    const loadTopics = async () => {
      try {
        const fetchedTopics = await getContactTopics();
        if (!mounted) return;
        setTopics(fetchedTopics);
        const preferredTopic = fetchedTopics[0]?.key ?? '';
        setForm((prev) => ({
          ...prev,
          topic: prev.topic || preferredTopic,
          selectedQuestion: undefined,
        }));
      } catch (error) {
        console.error('Failed to load contact topics', error);
        toast.error('Unable to load support options right now. Please refresh the page.');
      } finally {
        if (mounted) {
          setLoadingTopics(false);
        }
      }
    };

    loadTopics();
    return () => {
      mounted = false;
    };
  }, []);

  const selectedTopic = useMemo(
    () => topics.find((topic) => topic.key === form.topic),
    [topics, form.topic]
  );

  const handleChange = (
    key: keyof FormState,
    value: string | boolean | null | undefined
  ) => {
    setForm((prev) => {
      const next = {
        ...prev,
        [key]: value,
      } as FormState;

      if (key === 'topic') {
        next.topic = (value as string) || '';
        next.selectedQuestion = undefined;
      }

      return next;
    });
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!form.topic) {
      toast.error('Please choose the closest topic for your question.');
      return;
    }

    if (!form.selectedQuestion && (!form.message || form.message.trim().length < 12)) {
      toast.error('Add a quick note (12+ characters) or pick one of the suggested questions.');
      return;
    }

    setSubmitting(true);
    try {
      const response = await submitContactRequest({
        name: form.name.trim(),
        email: form.email.trim(),
        topic: form.topic,
        selected_question: form.selectedQuestion ?? undefined,
        message: form.message?.trim() || undefined,
        account_stage: form.accountStage || undefined,
        consent: form.consent,
      });

      toast.success(`${response.message} Reference #${response.reference_id}`);
      setForm((prev) => ({
        ...prev,
        selectedQuestion: undefined,
        message: '',
      }));
    } catch (error: any) {
      console.error('Failed to submit contact form', error);
      const detail = error?.response?.data?.detail;
      toast.error(detail || 'Unable to send your message. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-gradient-to-b from-white via-slate-50 to-slate-100 py-16 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <div className="mx-auto max-w-6xl px-6 lg:px-8">
        <header className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center rounded-full bg-blue-50 px-4 py-1 text-xs font-semibold uppercase tracking-wide text-blue-600 dark:bg-blue-500/15 dark:text-blue-200">
            Support Centre
          </span>
          <h1 className="mt-4 text-3xl font-bold text-slate-900 dark:text-slate-100 sm:text-4xl">
            We're here to help—tell us how we can support you
          </h1>
          <p className="mt-4 text-lg text-slate-600 dark:text-slate-300">
            Choose a pre-curated question or share a short note. Our customer success team replies within
            the defined SLA for each topic. Enterprise and security queries jump the queue automatically.
          </p>
        </header>

        <div className="mt-12 grid gap-10 lg:grid-cols-[1.1fr_0.9fr]">
          <section className="rounded-2xl bg-white shadow-xl shadow-slate-200/60 ring-1 ring-slate-200 dark:bg-slate-900/80 dark:shadow-slate-950/40 dark:ring-slate-800">
            <div className="border-b border-slate-200 px-6 py-5 dark:border-slate-800">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Send us a message</h2>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
                Fill out the short form below. You can pick a suggested question and add more context if needed.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6 px-6 py-6">
              <div className="grid gap-6 sm:grid-cols-2">
                <label className="flex flex-col gap-2">
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-200">Full name</span>
                  <input
                    type="text"
                    value={form.name}
                    onChange={(e) => handleChange('name', e.target.value)}
                    required
                    className={baseFieldClasses}
                    placeholder="Jane Doe"
                  />
                </label>
                <label className="flex flex-col gap-2">
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-200">Email</span>
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => handleChange('email', e.target.value)}
                    required
                    className={baseFieldClasses}
                    placeholder="you@company.com"
                  />
                </label>
              </div>

              <div className="grid gap-6 sm:grid-cols-2">
                <label className="flex flex-col gap-2">
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-200">Topic</span>
                  <select
                    value={form.topic}
                    onChange={(e) => handleChange('topic', e.target.value)}
                    className={baseFieldClasses}
                    disabled={loadingTopics}
                  >
                    {topics.map((topic) => (
                      <option key={topic.key} value={topic.key}>
                        {topic.title}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="flex flex-col gap-2">
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-200">Where are you in your journey?</span>
                  <select
                    value={form.accountStage || ''}
                    onChange={(e) => handleChange('accountStage', e.target.value || undefined)}
                    className={baseFieldClasses}
                  >
                    <option value="">Select an option (optional)</option>
                    {ACCOUNT_STAGE_OPTIONS.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              {selectedTopic && (
                <div>
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-200">Suggested questions</p>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    Choose one that captures your query. You can add more details below.
                  </p>
                  <div className="mt-3 flex flex-wrap gap-3">
                    {selectedTopic.faq_examples.map((question) => {
                      const isActive = question === form.selectedQuestion;
                      return (
                        <button
                          key={question}
                          type="button"
                          onClick={() =>
                            handleChange(
                              'selectedQuestion',
                              isActive ? undefined : question
                            )
                          }
                          className={`rounded-full border px-4 py-2 text-sm transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-300 ${
                            isActive
                              ? 'border-blue-500 bg-blue-50 text-blue-700 dark:border-blue-400 dark:bg-blue-500/20 dark:text-blue-100'
                              : 'border-slate-200 bg-white text-slate-600 hover:border-blue-300 hover:text-blue-600 dark:border-slate-700 dark:bg-slate-900/70 dark:text-slate-300 dark:hover:border-blue-400 dark:hover:text-blue-200'
                          }`}
                        >
                          {question}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              <label className="flex flex-col gap-2">
                <span className="text-sm font-medium text-slate-700 dark:text-slate-200">Additional details</span>
                <textarea
                  value={form.message}
                  onChange={(e) => handleChange('message', e.target.value)}
                  rows={6}
                  maxLength={2000}
                  className={`${baseFieldClasses} w-full min-h-[160px]`}
                  placeholder="Share a bit more context (optional)."
                />
                <span className="text-xs text-slate-400 dark:text-slate-500">
                  Minimum 12 characters if you skip the suggested questions. Max 2,000 characters.
                </span>
              </label>

              <label className="flex items-start gap-3 rounded-lg border border-slate-200 bg-slate-50 px-4 py-4 dark:border-slate-700 dark:bg-slate-900/70">
                <input
                  type="checkbox"
                  checked={form.consent}
                  onChange={(e) => handleChange('consent', e.target.checked)}
                  className="mt-1 h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900"
                />
                <span className="text-sm text-slate-600 dark:text-slate-300">
                  I agree to receive follow-up emails about this request. For more information, review our{' '}
                  <a href="/privacy" className="font-medium text-blue-600 hover:text-blue-700 dark:text-blue-300 dark:hover:text-blue-200" target="_blank" rel="noreferrer">
                    privacy policy
                  </a>
                  .
                </span>
              </label>

              <div className="flex flex-col gap-4 border-t border-slate-200 pt-6 sm:flex-row sm:items-center sm:justify-between dark:border-slate-800">
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Response time: {selectedTopic?.expected_response_hours ?? 12} hours · Priority routing based on topic
                </p>
                <button
                  type="submit"
                  disabled={submitting}
                  className="inline-flex items-center rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/30 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400 dark:shadow-blue-900/40"
                >
                  {submitting ? 'Sending…' : 'Send message'}
                </button>
              </div>
            </form>
          </section>

          <aside className="space-y-6">
            <div className="rounded-2xl bg-slate-900 p-8 text-slate-100 shadow-xl shadow-slate-900/40">
              <h3 className="text-lg font-semibold">Direct lines</h3>
              <p className="mt-2 text-sm text-slate-300">
                Prefer email? Reach us directly and we'll thread it into the same help desk workspace.
              </p>
              <div className="mt-6 space-y-4 text-sm">
                <div>
                  <p className="text-slate-400 uppercase tracking-wide text-xs">Support</p>
                  <a
                    href="mailto:tryreverseai@gmail.com"
                    className="mt-1 block text-base font-medium text-white hover:text-blue-200"
                  >
                    tryreverseai@gmail.com
                  </a>
                </div>
                <div>
                  <p className="text-slate-400 uppercase tracking-wide text-xs">Office Hours</p>
                  <p className="mt-1 text-base">Monday – Friday • 09:00 – 19:00 IST</p>
                  <p className="text-sm text-slate-400">Enterprise paging available 24/7 for severity-1 incidents.</p>
                </div>
                <div>
                  <p className="text-slate-400 uppercase tracking-wide text-xs">Registered office</p>
                  <p className="mt-1 text-base">Surat, India</p>
                  <p className="text-sm text-slate-400">Reverse AI Labs</p>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-lg shadow-slate-200/50 dark:border-slate-800 dark:bg-slate-900/80 dark:shadow-slate-950/50">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Service-level commitments</h3>
              <ul className="mt-4 space-y-3 text-sm text-slate-600 dark:text-slate-300">
                <li className="flex items-start gap-3">
                  <span className="mt-1 inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
                  <span>
                    <strong className="text-slate-800 dark:text-slate-100">General enquiries:</strong> 12 business hours response, follow-up until closure.
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="mt-1 inline-flex h-2.5 w-2.5 rounded-full bg-amber-500"></span>
                  <span>
                    <strong className="text-slate-800 dark:text-slate-100">Billing or integration issues:</strong> 8 business hours triage, real-time escalation if revenue-impacting.
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="mt-1 inline-flex h-2.5 w-2.5 rounded-full bg-rose-500"></span>
                  <span>
                    <strong className="text-slate-800 dark:text-slate-100">Security disclosures:</strong> 4 hour acknowledgment, coordinated remediation with our security team.
                  </span>
                </li>
              </ul>
              <p className="mt-5 text-xs text-slate-400 dark:text-slate-500">
                By submitting this form you confirm that you have reviewed our Terms of Service and Privacy Policy and agree to be contacted regarding your request.
              </p>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
};

export default ContactPage;
