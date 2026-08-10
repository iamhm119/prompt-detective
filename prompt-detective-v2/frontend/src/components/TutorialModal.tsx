import React, { useEffect, useState } from 'react';
import {
  X,
  ArrowLeft,
  ArrowRight,
  Upload,
  Eye,
  History,
  Settings,
  CheckCircle,
  Sparkles,
  MonitorPlay,
  Wand2,
  ShieldCheck,
  Copy,
} from 'lucide-react';

interface TutorialStep {
  id: number;
  title: string;
  description: string;
  icon: React.ReactNode;
  target?: string;
  content: string;
}

interface TutorialModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

const TutorialModal: React.FC<TutorialModalProps> = ({ isOpen, onClose, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isCompleting, setIsCompleting] = useState(false);

  const tutorialSteps: TutorialStep[] = [
    {
      id: 1,
      title: 'Welcome to Prompt Detective',
      description: 'Tour the essentials in under a minute',
      icon: <Sparkles className="w-8 h-8 text-indigo-400" />,
      content:
        'Thanks for joining our creative intelligence workspace. This quick walkthrough shows how to upload confidently, monitor live analysis, and export production-ready prompt packets.'
    },
    {
      id: 2,
      title: 'Calibrate your first upload',
      description: 'Drag & drop, paste a link, or browse files',
      icon: <Upload className="w-8 h-8 text-blue-500" />,
      target: 'upload-area',
      content:
        'Use the dashboard hero to add MP4, MOV, or imagery up to 5 minutes in length. We fingerprint scenes, detect camera notes, and prep the pipeline the moment your file lands.'
    },
    {
      id: 3,
      title: 'Watch the live pipeline',
      description: 'Every stage is observable and timestamped',
      icon: <Eye className="w-8 h-8 text-purple-500" />,
      content:
        'Progress toasts, breadcrumbs, and a realtime timeline surface upload, frame extraction, and AI insights as they happen—perfect for briefing stakeholders without leaving the screen.'
    },
    {
      id: 4,
      title: 'Inspect prompt intelligence',
      description: 'Deep dives tailored to creative and compliance teams',
      icon: <Settings className="w-8 h-8 text-orange-400" />,
      content:
        'Results include reconstructed prompts, lighting + camera modifiers, recommended models, and provenance signals. Copy, export, or hand off to teammates in one click.'
    },
    {
      id: 5,
      title: 'History & collaboration hub',
      description: 'Everything saved, searchable, and shareable',
      icon: <History className="w-8 h-8 text-teal-400" />,
      content:
        'Browse thumbnails, filter by status, compare prompt iterations, and download audit-friendly dossiers. Invite teammates to comment or trigger automations directly from the timeline.'
    },
    {
      id: 6,
      title: 'Launch your workspace',
      description: 'Secure, encrypted, and ready for production',
      icon: <ShieldCheck className="w-8 h-8 text-emerald-400" />,
      content:
        'We apply zero-retention processing and SOC2-ready controls behind the scenes. Start analysing now or revisit the tour anytime from the Product Tour button in the top navigation.'
    }
  ];

  const handleNext = () => {
    if (currentStep < tutorialSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    setIsCompleting(true);

    setTimeout(() => {
      onComplete();
      setIsCompleting(false);
      setCurrentStep(0);
    }, 1200);
  };

  const handleSkip = () => {
    onClose();
    setCurrentStep(0);
  };

  useEffect(() => {
    if (isOpen) {
      setCurrentStep(0);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const step = tutorialSteps[currentStep];
  const isLastStep = currentStep === tutorialSteps.length - 1;
  const isFirstStep = currentStep === 0;
  const completion = Math.round(((currentStep + 1) / tutorialSteps.length) * 100);

  return (
    <div className="fixed inset-0 z-[120] flex items-center justify-center bg-slate-950/80 px-3 py-6 backdrop-blur-[8px] sm:px-4 sm:py-8">
      <div className="relative flex w-full max-w-4xl flex-col overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-slate-900/90 via-slate-950/85 to-slate-950/95 shadow-[0_40px_120px_-40px_rgba(56,189,248,0.45)]">
        <div className="pointer-events-none absolute -top-32 left-1/3 h-72 w-72 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-indigo-500/20 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-16 right-0 h-52 w-52 rounded-full bg-violet-500/20 blur-3xl" />

        <div className="relative grid max-h-[85vh] gap-6 overflow-y-auto p-6 md:p-8 lg:grid-cols-[280px,minmax(0,1fr)]">
          <aside className="flex flex-col gap-6 rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-inner shadow-cyan-500/10">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.4em] text-cyan-200/70">Product tour</p>
                <h2 className="mt-2 text-2xl font-semibold text-white">Prompt Detective overview</h2>
              </div>
              <button
                onClick={handleSkip}
                className="rounded-full bg-white/5 p-2 text-slate-300 transition hover:bg-white/10 hover:text-white"
                aria-label="Skip tour"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-4">
              {tutorialSteps.map((item, index) => {
                const state = index === currentStep ? 'active' : index < currentStep ? 'complete' : 'upcoming';
                return (
                  <button
                    key={item.id}
                    onClick={() => setCurrentStep(index)}
                    className={`group flex w-full items-center gap-4 rounded-2xl border border-transparent px-3 py-3 text-left transition duration-200 ${
                      state === 'active'
                        ? 'bg-cyan-500/15 border-cyan-400/60 shadow-[0_10px_35px_-20px_rgba(6,182,212,0.65)]'
                        : state === 'complete'
                        ? 'bg-white/5 text-slate-200 hover:border-white/10'
                        : 'text-slate-400 hover:bg-white/5'
                    }`}
                  >
                    <span
                      className={`flex h-10 w-10 items-center justify-center rounded-xl text-sm font-semibold transition ${
                        state === 'active'
                          ? 'bg-gradient-to-br from-cyan-400 to-blue-500 text-slate-900'
                          : state === 'complete'
                          ? 'bg-emerald-400/20 text-emerald-200'
                          : 'bg-white/5 text-slate-400'
                      }`}
                    >
                      {index + 1}
                    </span>
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-white/90">{item.title}</p>
                      <p className="text-xs text-slate-400">{item.description}</p>
                    </div>
                    {state === 'complete' && (
                      <CheckCircle className="h-4 w-4 text-emerald-300" />
                    )}
                  </button>
                );
              })}
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-xs text-slate-300">
              <p className="font-semibold uppercase tracking-wide text-cyan-200">PRO TIP</p>
              <p className="mt-2 text-slate-200">
                Need to revisit later? You can relaunch the tour anytime from the Product Tour button in the top navigation.
              </p>
            </div>
          </aside>

          <section className="flex flex-col justify-between rounded-3xl border border-white/10 bg-white/10 p-6 backdrop-blur-xl md:p-8">
            <header className="flex items-start justify-between gap-6">
              <div className="flex items-center gap-4">
                <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 to-blue-500 text-slate-900 shadow-lg shadow-cyan-500/30">
                  {step.icon}
                </span>
                <div>
                  <h3 className="text-2xl font-semibold text-slate-900 dark:text-white">{step.title}</h3>
                  <p className="text-sm text-slate-600 dark:text-slate-300">{step.description}</p>
                </div>
              </div>
              <div className="hidden rounded-full bg-white/70 px-4 py-2 text-xs font-semibold text-slate-600 dark:bg-slate-900/50 dark:text-slate-200 lg:flex lg:flex-col lg:text-right">
                <span>Progress</span>
                <span className="text-sm text-slate-900 dark:text-white">{completion}%</span>
              </div>
            </header>

            <div className="mt-8 space-y-6 text-sm leading-relaxed text-slate-700 dark:text-slate-200">
              <p className="rounded-2xl border border-white/30 bg-white/70 px-5 py-4 shadow-inner shadow-cyan-200/20 dark:bg-slate-900/60 dark:text-slate-100">
                {step.content}
              </p>

              {currentStep === 0 && (
                <div className="grid gap-4 rounded-2xl border border-cyan-200/40 bg-cyan-500/10 p-4 text-xs text-cyan-900 dark:border-cyan-400/20 dark:bg-cyan-500/5 dark:text-cyan-100 sm:grid-cols-2">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4" />
                    AI co-pilot for visual forensics
                  </div>
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="h-4 w-4" />
                    Privacy-focused, secure processing
                  </div>
                  <div className="flex items-center gap-2">
                    <MonitorPlay className="h-4 w-4" />
                    Video + image reverse engineering
                  </div>
                  <div className="flex items-center gap-2">
                    <Wand2 className="h-4 w-4" />
                    Prompt enhancements & presets
                  </div>
                </div>
              )}

              {currentStep === 1 && (
                <div className="grid gap-4 rounded-2xl border border-blue-300/40 bg-blue-500/10 p-5 text-xs text-blue-900 dark:border-blue-400/20 dark:bg-blue-500/5 dark:text-blue-100 sm:grid-cols-2">
                  <div className="rounded-xl border border-white/20 bg-white/30 p-4 dark:bg-slate-900/40">
                    <p className="text-[11px] uppercase tracking-wide text-blue-700 dark:text-blue-200">Video formats</p>
                    <p className="mt-1 font-semibold">MP4 · MOV · AVI</p>
                    <p className="mt-2 text-[11px] text-blue-800/70 dark:text-blue-100/70">Up to 5 minutes — auto scene detection included.</p>
                  </div>
                  <div className="rounded-xl border border-white/20 bg-white/30 p-4 dark:bg-slate-900/40">
                    <p className="text-[11px] uppercase tracking-wide text-blue-700 dark:text-blue-200">Image formats</p>
                    <p className="mt-1 font-semibold">JPG · PNG · WEBP · GIF</p>
                    <p className="mt-2 text-[11px] text-blue-800/70 dark:text-blue-100/70">Smart compression keeps clarity for accurate prompts.</p>
                  </div>
                </div>
              )}

              {currentStep === 2 && (
                <div className="rounded-2xl border border-purple-300/40 bg-purple-500/10 p-5 text-xs text-purple-900 dark:border-purple-400/20 dark:bg-purple-500/5 dark:text-purple-100">
                  <p className="text-[11px] uppercase tracking-wide text-purple-700 dark:text-purple-200">Pipeline highlights</p>
                  <ul className="mt-3 space-y-2">
                    <li className="flex items-start gap-2">
                      <span className="mt-1 h-2 w-2 rounded-full bg-purple-400" />
                      Frame-level semantic tagging for motion and lighting cues.
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="mt-1 h-2 w-2 rounded-full bg-purple-400" />
                      Adaptive AI heuristics based on media type and complexity.
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="mt-1 h-2 w-2 rounded-full bg-purple-400" />
                      Confidence scoring to benchmark prompt certainty.
                    </li>
                  </ul>
                </div>
              )}

              {currentStep === 3 && (
                <div className="rounded-2xl border border-orange-300/40 bg-orange-500/10 p-5 text-xs text-orange-900 dark:border-orange-400/20 dark:bg-orange-500/5 dark:text-orange-100">
                  <p className="text-[11px] uppercase tracking-wide text-orange-700 dark:text-orange-200">Deliverables</p>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <div className="rounded-xl border border-white/20 bg-white/40 p-4 dark:bg-slate-900/40">
                      <p className="text-[11px] uppercase tracking-wide text-orange-800 dark:text-orange-300">Prompt packet</p>
                      <p className="mt-2 text-sm">Primary prompt, enhancement modifiers, model tips.</p>
                    </div>
                    <div className="rounded-xl border border-white/20 bg-white/40 p-4 dark:bg-slate-900/40">
                      <p className="text-[11px] uppercase tracking-wide text-orange-800 dark:text-orange-300">Export options</p>
                      <p className="mt-2 text-sm">TXT, JSON, CSV with share-ready formatting.</p>
                    </div>
                  </div>
                </div>
              )}

              {currentStep === 4 && (
                <div className="rounded-2xl border border-emerald-300/40 bg-emerald-500/10 p-5 text-xs text-emerald-900 dark:border-emerald-400/20 dark:bg-emerald-500/5 dark:text-emerald-100">
                  <p className="text-[11px] uppercase tracking-wide text-emerald-700 dark:text-emerald-200">History workspace</p>
                  <ul className="mt-3 space-y-2">
                    <li className="flex items-center gap-2">
                      <History className="h-4 w-4" />
                      Rich thumbnails + prompt previews at a glance.
                    </li>
                    <li className="flex items-center gap-2">
                      <Sparkles className="h-4 w-4" />
                      Filter by status, format, or enhancement features.
                    </li>
                    <li className="flex items-center gap-2">
                      <Copy className="h-4 w-4" />
                      One-click export into your creative workflow.
                    </li>
                  </ul>
                </div>
              )}

              {currentStep === 5 && (
                <div className="rounded-2xl border border-emerald-300/40 bg-emerald-500/10 p-5 text-xs text-emerald-900 dark:border-emerald-400/20 dark:bg-emerald-500/5 dark:text-emerald-100">
                  <p className="text-[11px] uppercase tracking-wide text-emerald-700 dark:text-emerald-200">Launch checklist</p>
                  <ul className="mt-3 space-y-2 text-sm">
                    <li>1. Upload a reference asset from the dashboard hero row or paste a secure URL.</li>
                    <li>2. Invite collaborators from the top nav to share timelines and exports.</li>
                    <li>3. Enable advanced alerts in Settings → Notifications for high-signal jobs.</li>
                  </ul>
                </div>
              )}
            </div>

            <footer className="mt-10 flex flex-col gap-4 border-t border-white/20 pt-6 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-300">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500/30 to-blue-500/30 text-cyan-100">
                  <Sparkles className="h-4 w-4" />
                </div>
                <div>
                  <p className="font-semibold text-slate-700 dark:text-slate-200">Step {currentStep + 1} of {tutorialSteps.length}</p>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">{completion}% complete • Guided onboarding</p>
                </div>
              </div>

              <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                <button
                  onClick={handlePrevious}
                  disabled={isFirstStep}
                  className={`inline-flex items-center justify-center gap-2 rounded-full border px-5 py-2 text-sm transition ${
                    isFirstStep
                      ? 'cursor-not-allowed border-white/10 text-slate-500'
                      : 'border-white/30 text-slate-200 hover:bg-white/10'
                  }`}
                >
                  <ArrowLeft className="h-4 w-4" />
                  Previous
                </button>

                <button
                  onClick={handleNext}
                  className="inline-flex items-center justify-center gap-2 rounded-full bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-500 px-7 py-2 text-sm font-semibold text-slate-900 shadow-lg shadow-cyan-500/40 transition hover:shadow-cyan-500/50"
                >
                  <span>{isLastStep ? 'Launch workspace' : 'Next step'}</span>
                  {isLastStep ? <CheckCircle className="h-4 w-4" /> : <ArrowRight className="h-4 w-4" />}
                </button>
              </div>
            </footer>

            {isCompleting && (
              <div className="pointer-events-none absolute inset-0 flex items-center justify-center rounded-3xl bg-slate-900/70 backdrop-blur-xl">
                <div className="flex flex-col items-center gap-4 text-center text-slate-200">
                  <div className="relative">
                    <div className="h-14 w-14 animate-spin rounded-full border-4 border-cyan-400/50 border-t-transparent" />
                    <Sparkles className="absolute inset-0 m-auto h-6 w-6 text-cyan-300" />
                  </div>
                  <p className="text-lg font-semibold">Setting up your workspace…</p>
                  <p className="text-sm text-slate-400">We’ll take you straight to the dashboard.</p>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
};

export default TutorialModal;