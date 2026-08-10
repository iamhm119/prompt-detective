import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useUpload } from '../hooks/useUpload';
import { UploadComponent } from '../components/UploadComponent';
import PageHeader from '../components/PageHeader';
import BentoGrid, { BentoItem } from '../components/ui/BentoGrid';
import Card from '../components/ui/Card';
import Carousel, { CarouselItem } from '../components/ui/Carousel';
import Accordion, { AccordionItem } from '../components/ui/Accordion';
import Chip from '../components/ui/Chip';
import { Button } from '../components/ui/Button';
import Skeleton from '../components/ui/Skeleton';
import { Sparkles, Upload, ShieldCheck, Timer, Workflow, Languages, Rocket, Wand2 } from 'lucide-react';

const LandingPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { uploadFile } = useUpload();
  const [trialJobId, setTrialJobId] = useState<string | null>(null);

  const testimonials = useMemo<CarouselItem[]>(
    () => [
      {
        id: 'creative-director',
        content: (
          <div className="space-y-3">
            <p className="text-lg font-medium text-gray-900 dark:text-white">“It feels like having an AI sommelier for visuals.”</p>
            <p className="text-sm text-gray-500 dark:text-white/80">
              We upload moodboards and Prompt Detective returns narrative-ready prompts with style chips I can share with my team.
            </p>
            <div className="flex items-center justify-between text-sm text-gray-400 dark:text-white/70">
              <span>— Maya Laurent, Creative Director @ Helix Studio</span>
              <Chip tone="blue" size="sm">12x faster reviews</Chip>
            </div>
          </div>
        ),
      },
      {
        id: 'product-team',
        content: (
          <div className="space-y-3">
            <p className="text-lg font-medium text-gray-900 dark:text-white">“Breadcrumbs + toasts keep stakeholders calm.”</p>
            <p className="text-sm text-gray-500 dark:text-white/80">
              The dashboard mirrors Apple-quality UX—snackbars signal every milestone, skeletons avoid blank states, and legal gets audit-ready exports.
            </p>
            <div className="flex items-center justify-between text-sm text-gray-400 dark:text-white/70">
              <span>— Amir Patel, Product Lead @ Renderlight</span>
              <Chip tone="purple" size="sm">Loved by compliance</Chip>
            </div>
          </div>
        ),
      },
      {
        id: 'filmmaker',
        content: (
          <div className="space-y-3">
            <p className="text-lg font-medium text-gray-900 dark:text-white">“The carousel of scene prompts is literally our storyboard.”</p>
            <p className="text-sm text-gray-500 dark:text-white/80">
              We shoot reference reels, upload, and get dynamic prompt chips we can iterate with instantly.
            </p>
            <div className="flex items-center justify-between text-sm text-gray-400 dark:text-white/70">
              <span>— Lucia Bonneville, Cinematographer</span>
              <Chip tone="emerald" size="sm">Cuts ideation to 15 min</Chip>
            </div>
          </div>
        ),
      },
    ],
    []
  );

  const bentoItems = useMemo<BentoItem[]>(
    () => [
      {
        key: 'creative-lab',
        title: 'Creative labs',
        description: 'Translate trend references into production-ready prompts with context about camera moves, lighting, and mood.',
        icon: <Sparkles className="h-6 w-6 text-indigo-500" />,
        footer: 'Sync with Figma, Motion, or Final Cut',
        accent: 'purple',
      },
      {
        key: 'brand-qa',
        title: 'Brand QA teams',
        description: 'Audit user-generated content for alignment with your brand palette, subject matter, and stylistic guardrails.',
        icon: <ShieldCheck className="h-6 w-6 text-emerald-500" />,
        footer: 'Watermark & metadata detection baked in',
        accent: 'emerald',
      },
      {
        key: 'growth',
        title: 'Growth marketers',
        description: 'Reverse engineer high-performing ads to recreate eye-catching compositions with confidence.',
        icon: <Rocket className="h-6 w-6 text-blue-500" />,
        footer: 'Turn analysis into remixable prompt chips',
        accent: 'blue',
      },
      {
        key: 'localization',
        title: 'Localization teams',
        description: 'Translate prompt semantics across languages while preserving nuance and cultural context.',
        icon: <Languages className="h-6 w-6 text-amber-500" />,
        footer: 'Automatic tone + cultural sensitivity checks',
        accent: 'amber',
      },
      {
        key: 'research',
        title: 'Research & ethics',
        description: 'Inspect dataset bias, detect model fingerprints, and export documentation for review boards.',
        icon: <Workflow className="h-6 w-6 text-purple-500" />,
        footer: 'Generate shareable audit dossiers',
        accent: 'purple',
      },
      {
        key: 'indie',
        title: 'Indie builders',
        description: 'Automate daily inspiration emails with curated prompt ideas and moodboard-ready frames.',
        icon: <Wand2 className="h-6 w-6 text-rose-500" />,
        footer: 'Hooks into Zapier & Notion in one click',
        accent: 'blue',
      },
    ],
    []
  );

  const faqItems = useMemo<AccordionItem[]>(
    () => [
      {
        id: 'formats',
        title: 'Which formats can I upload?',
        helperText: 'Images up to 80 MB, videos up to 300 MB on growth plans.',
        description: (
          <ul className="list-disc space-y-2 pl-5 text-sm text-gray-600 dark:text-white/80">
            <li>Video: MP4, MOV, WEBM up to 4K resolution.</li>
            <li>Image: PNG, JPG, WEBP, TIFF with transparent background support.</li>
            <li>We automatically snapshot key frames and show skeleton loading for each stage.</li>
          </ul>
        ),
      },
      {
        id: 'security',
        title: 'How do you keep my uploads secure?',
        helperText: 'Private by default—no public galleries.',
        description: (
          <p className="text-gray-600 dark:text-white/80">
            Files are encrypted at rest, scrubbed after 48 hours, and processed on isolated workers. Our audit logs with breadcrumb navigation give you full traceability.
          </p>
        ),
      },
      {
        id: 'sharing',
        title: 'Can I share results with collaborators?',
        helperText: 'Yes—add collaborators or send read-only links.',
        description: (
          <p className="text-gray-600 dark:text-white/80">
            Invite teammates with granular permissions. They receive real-time snackbars when new analyses finish and can add annotations directly in the prompt timeline.
          </p>
        ),
      },
      {
        id: 'speed',
        title: 'What is the average processing time?',
        helperText: 'Under 90 seconds for most jobs.',
        description: (
          <p className="text-gray-600 dark:text-white/80">
            Our adaptive queue warms engines in advance. Skeleton loaders bridge any delay, and toasts highlight progress (upload → extraction → AI insights → prompt export).
          </p>
        ),
      },
    ],
    []
  );

  const handleTrialUpload = async (file: File) => {
    try {
      const response = await uploadFile(file);
      setTrialJobId(response.job_id);
    } catch (error) {
      console.error('Trial upload failed:', error);
    }
  };

  return (
    <div className="space-y-20 pb-24">
      <section>
        <PageHeader
          title="Reverse engineer AI visuals with poetic precision"
          subtitle="Upload any image or motion clip to uncover the hidden prompt architecture, key styles, and production guidance behind it."
          breadcrumbs={[{ label: 'Home' }]}
          primaryAction={{ label: isAuthenticated ? 'Open dashboard' : 'Start free trial', onClick: () => { /* routed via Link buttons below */ } }}
          secondaryAction={{ label: 'See pricing breakdown', onClick: () => { window.location.href = '/pricing'; } }}
          illustration={<Sparkles className="h-16 w-16 text-indigo-500" />}
        />
  <div className="mt-6 flex flex-wrap gap-4 text-sm text-gray-500 dark:text-white/80">
          <Chip tone="blue">No credit card required</Chip>
          <Chip tone="purple">Live job tracking</Chip>
          <Chip tone="emerald">Supports MP4, MOV, PNG, JPG</Chip>
        </div>
        <div className="mt-10 grid gap-8 lg:grid-cols-[1.2fr,0.8fr]">
          <Card variant="translucent" padding="lg" interactive className="relative">
            <div className="flex flex-col gap-6">
              <div className="flex flex-wrap gap-3">
                <Button size="lg" component={Link} to={isAuthenticated ? '/dashboard' : '/signup'}>
                  {isAuthenticated ? 'Go to dashboard' : 'Create a free account'}
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  component={Link}
                  to="/pricing"
                >
                  Explore plans
                </Button>
              </div>
              <Card variant="outline" padding="md" className="bg-white/90 dark:bg-slate-900/80">
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-600 dark:bg-indigo-500/20 dark:text-indigo-200">
                    <Upload className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">Immediate feedback</p>
                    <p className="text-sm text-gray-500 dark:text-white/80">Receive smart toast updates while each stage of analysis completes.</p>
                  </div>
                </div>
              </Card>
              <Carousel
                items={testimonials}
                className="bg-white/90 dark:bg-slate-900/80"
              />
            </div>
          </Card>
          <Card variant="elevated" padding="md" className="relative overflow-hidden">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-blue-500 dark:text-indigo-200">Try Prompt Detective </p>
                <h2 className="mt-2 text-xl font-semibold text-gray-900 dark:text-white">Upload once. Trace every layer.</h2>
              </div>
              <Chip tone="purple" size="sm">Live demo</Chip>
            </div>
            <Skeleton className="h-60 rounded-2xl" />
            <p className="mt-4 text-sm text-gray-500 dark:text-white/80">Adaptive skeleton loading appears while we warm up your model runner—no blank states.</p>
          </Card>
        </div>
      </section>

      {!isAuthenticated && (
        <section id="trial" className="space-y-10">
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-3xl font-semibold text-gray-900 dark:text-white">Try a production-grade analysis without signing in</h2>
              <p className="mt-2 max-w-2xl text-gray-500 dark:text-white/80">
                We reserve a spot in the queue for your trial upload. Your results persist for 24 hours so you can review before creating an account.
              </p>
            </div>
            <Button variant="outline" size="lg" component={Link} to="/pricing">
              Compare plan limits
            </Button>
          </div>
          <Card variant="outline" padding="lg" className="bg-gradient-to-br from-white via-white to-blue-50/40 dark:from-slate-900/85 dark:via-slate-900/70 dark:to-indigo-950/40">
            <UploadComponent
              onUpload={handleTrialUpload}
              maxFileSize={50 * 1024 * 1024}
              acceptedTypes={['image/*', 'video/*']}
              disabled={false}
            />
            {trialJobId && (
              <div className="mt-6 rounded-2xl border border-blue-100 bg-blue-50/70 p-4 text-sm text-blue-700 dark:border-indigo-500/30 dark:bg-indigo-500/10 dark:text-white/85">
                ⚡ Your analysis is running in a sandbox. Job reference: {trialJobId}
              </div>
            )}
          </Card>
        </section>
      )}

      <section className="space-y-10">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white">Crafted for ambitious teams</h2>
            <p className="mt-2 max-w-2xl text-gray-500 dark:text-white/80">Bento grid of scenarios we support—from creative teams to compliance squads tracking AI provenance.</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Chip tone="gray" size="sm">Creative direction</Chip>
            <Chip tone="blue" size="sm">Brand QA</Chip>
            <Chip tone="emerald" size="sm">Compliance</Chip>
            <Chip tone="purple" size="sm">Prompt R&D</Chip>
          </div>
        </div>
        <BentoGrid items={bentoItems} className="lg:grid-cols-3" />
      </section>

      <section className="space-y-10">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <h2 className="text-3xl font-semibold text-gray-900 dark:text-white">Highlights that feel native</h2>
          <Button variant="outline" size="sm" component={Link} to="/coming-soon">
            Upcoming releases
          </Button>
        </div>
        <div className="grid gap-6 lg:grid-cols-3">
          <Card variant="translucent" padding="md">
            <div className="flex items-center gap-3">
              <ShieldCheck className="h-6 w-6 text-emerald-500 dark:text-emerald-300" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Prompt provenance</h3>
            </div>
            <p className="mt-3 text-sm text-gray-500 dark:text-white/80">We surface watermark traces, metadata drift, and AI model fingerprints so you can trust the prompt lineage.</p>
          </Card>
          <Card variant="translucent" padding="md">
            <div className="flex items-center gap-3">
              <Timer className="h-6 w-6 text-blue-500 dark:text-indigo-300" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Instant snack bars</h3>
            </div>
            <p className="mt-3 text-sm text-gray-500 dark:text-white/80">Toast + snackbar combo quietly informs you when frame extraction starts, finishes, and when AI narration is ready.</p>
          </Card>
          <Card variant="translucent" padding="md">
            <div className="flex items-center gap-3">
              <Workflow className="h-6 w-6 text-purple-500 dark:text-indigo-300" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Guided breadcrumbs</h3>
            </div>
            <p className="mt-3 text-sm text-gray-500 dark:text-white/80">Every multi-step flow—from sign-up to results—uses contextual breadcrumbs so users never feel lost.</p>
          </Card>
        </div>
      </section>

      <section className="space-y-6" id="faq">
        <div className="flex flex-col gap-2">
          <h2 className="text-3xl font-semibold text-gray-900 dark:text-white">Frequently asked</h2>
          <p className="max-w-2xl text-gray-500 dark:text-white/80">Expand each accordion to see how our team handles data, privacy, and performance pledges.</p>
        </div>
        <Accordion items={faqItems} defaultOpenId="sharing" />
      </section>

      <section className="rounded-[32px] border border-white/60 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 p-10 text-white shadow-[0_30px_90px_-40px_rgba(37,99,235,0.65)]">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <Chip tone="gray" pill={false} className="border-white/30 bg-white/10 text-white">
              Daily inspiration digest
            </Chip>
            <h2 className="mt-4 text-3xl font-semibold">Stay ahead with AI creative intelligence</h2>
            <p className="mt-2 max-w-xl text-blue-100">From marketing squads to indie artists, collect story-ready prompts, provenance highlights, and workflow tips in your inbox.</p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Button size="lg" variant="secondary" component={Link} to={isAuthenticated ? '/dashboard' : '/signup'}>
              {isAuthenticated ? 'Resume analyzing' : 'Start free trial'}
            </Button>
            <Button size="lg" variant="ghost" component={Link} to="/contact" className="text-white hover:bg-white/10">
              Talk to product team
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;