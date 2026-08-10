import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Check,
  Clock,
  Copy,
  Download,
  Eye,
  Film,
  History,
  Image as ImageIcon,
  Loader2,
  Sparkles,
  Upload,
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useUpload } from '../hooks/useUpload';
import { UploadComponent } from '../components/UploadComponent';
import ProgressModal from '../components/ProgressModal';
import UsageStatus from '../components/UsageStatus';
import JobResultModal from '../components/JobResultModal';
import PageContainer from '../components/page/PageContainer';
import PageSection from '../components/page/PageSection';
import PageHeader from '../components/PageHeader';
import Card from '../components/ui/Card';
import Chip from '../components/ui/Chip';
import { Button } from '../components/ui/Button';
import { useUiStore } from '../stores/uiStore';

interface JobResult {
  job_id: string;
  filename: string;
  content_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  main_prompt?: string;
  prompt_preview?: string;
  summary?: {
    content_type: string;
    duration?: number;
    resolution?: string;
    fps?: number;
    frames_analyzed?: number;
    analysis_method?: string;
    enhancement_features?: string[];
  };
  enhancement_features?: string[];
  has_full_prompt?: boolean;
  analysis_quality?: {
    has_enhancement_features: boolean;
    has_detailed_analysis: boolean;
    analysis_timestamp: string;
    processing_successful: boolean;
  };
  error?: string;
  error_message?: string;
  created_at: string;
  completed_at?: string;
  processing_time_seconds?: number;
  thumbnail_url?: string;
}

const statusConfig = (status?: JobResult['status']) => {
  switch (status) {
    case 'completed':
      return { label: 'Completed', tone: 'emerald' as const };
    case 'processing':
      return { label: 'Processing', tone: 'amber' as const };
    case 'pending':
      return { label: 'Queued', tone: 'blue' as const };
    case 'failed':
      return { label: 'Failed', tone: 'rose' as const };
    default:
      return { label: 'Unknown', tone: 'gray' as const };
  }
};

const formatDate = (value: string) => {
  try {
    return new Date(value).toLocaleString(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    });
  } catch (error) {
    return value;
  }
};

const formatProcessingTime = (seconds?: number) => {
  if (!seconds) return '—';
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds}s`;
};

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const { uploadFile, listJobs } = useUpload();
  const navigate = useNavigate();
  const uploadRef = useRef<HTMLDivElement>(null);
  const [recentAnalyses, setRecentAnalyses] = useState<JobResult[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [activeJobInfo, setActiveJobInfo] = useState<{ filename: string; contentType: string } | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobResult | null>(null);
  const [showJobModal, setShowJobModal] = useState(false);
  const [copiedPrompt, setCopiedPrompt] = useState<string | null>(null);
  const { openTutorial } = useUiStore();

  useEffect(() => {
    if (!user?.id) {
      return;
    }

    const tutorialKey = `hasSeenTutorial_${user.id}`;
    const hasSeenTutorial = localStorage.getItem(tutorialKey);

    if (!hasSeenTutorial) {
      const timeout = setTimeout(() => openTutorial('auto'), 500);
      return () => clearTimeout(timeout);
    }

    return undefined;
  }, [openTutorial, user?.id]);

  useEffect(() => {
    loadRecentJobs();
  }, []);

  const loadRecentJobs = async () => {
    try {
      setIsLoadingHistory(true);
      const response = await listJobs('', 5, 0);
      if (response.jobs) {
        setRecentAnalyses(response.jobs);
      }
    } catch (error) {
      console.error('Failed to load jobs:', error);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const handleUpload = async (file: File) => {
    try {
      const tempJobId = `temp_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`;
      setActiveJobInfo({ filename: file.name, contentType: file.type });
      setActiveJobId(tempJobId);

      const response = await uploadFile(file);
      const realJobId = response.job_id || (response as any).id || (response as any).jobId;

      if (realJobId) {
        setActiveJobId(String(realJobId));
        setTimeout(loadRecentJobs, 1000);
      } else {
        setActiveJobId(null);
        setActiveJobInfo(null);
      }
    } catch (error) {
      console.error('Upload failed:', error);
      setActiveJobId(null);
      setActiveJobInfo(null);
    }
  };

  const handleJobComplete = () => {
    setActiveJobId(null);
    setActiveJobInfo(null);
    loadRecentJobs();
  };

  const handleViewJob = (job: JobResult) => {
    setSelectedJob(job);
    setShowJobModal(true);
  };

  const handleCopyPrompt = async (prompt: string, jobId: string) => {
    try {
      await navigator.clipboard.writeText(prompt);
      setCopiedPrompt(jobId);
      setTimeout(() => setCopiedPrompt(null), 2000);
    } catch (error) {
      console.error('Failed to copy prompt:', error);
    }
  };

  const handleDownloadPrompt = (job: JobResult) => {
    if (!job.main_prompt) return;
    const blob = new Blob([job.main_prompt], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `${job.filename}_prompt.txt`;
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);
  };

  const stats = useMemo(() => {
    const completedJobs = recentAnalyses.filter((job) => job.status === 'completed').length;
    const processingJobs = recentAnalyses.filter((job) => job.status === 'processing' || job.status === 'pending').length;
    const processingTimes = recentAnalyses.filter((job) => typeof job.processing_time_seconds === 'number');
    const avgProcessingTime =
      processingTimes.reduce((acc, job) => acc + (job.processing_time_seconds || 0), 0) /
      Math.max(1, processingTimes.length);

    return {
      completedJobs,
      processingJobs,
      avgProcessingTime: Math.round(avgProcessingTime),
      totalTracked: recentAnalyses.length,
    };
  }, [recentAnalyses]);

  const highlightCards = useMemo(
    () => [
      {
        key: 'completed',
        label: 'Recent completions',
        value: stats.completedJobs,
        helper: 'Past five uploads',
        icon: <Check className="h-5 w-5 text-emerald-500" />,
      },
      {
        key: 'processing',
        label: 'In flight',
        value: stats.processingJobs,
        helper: 'Live in the queue',
        icon: <Clock className="h-5 w-5 text-amber-500" />,
      },
      {
        key: 'average',
        label: 'Average processing',
        value: stats.avgProcessingTime ? `${stats.avgProcessingTime}s` : '—',
        helper: 'Across recent jobs',
        icon: <Sparkles className="h-5 w-5 text-indigo-500" />,
      },
      {
        key: 'tracked',
        label: 'Jobs tracked',
        value: stats.totalTracked,
        helper: 'Latest refresh window',
        icon: <History className="h-5 w-5 text-blue-500" />,
      },
    ],
    [stats]
  );

  return (
    <PageContainer>
      <PageHeader
        title={`Welcome back, ${user?.full_name || user?.email || 'Creator'}`}
        subtitle="Reverse engineer visuals with cinematic insight, track every upload, and export shareable prompts in seconds."
        breadcrumbs={[{ label: 'Dashboard' }]}
        primaryAction={{
          label: 'Upload asset',
          onClick: () => uploadRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
        }}
        secondaryAction={{
          label: 'View history',
          onClick: () => navigate('/history'),
        }}
        illustration={<Sparkles className="h-12 w-12 text-indigo-500" />}
      />

      <div className="flex flex-wrap gap-3 text-sm text-gray-500 dark:text-slate-400">
        <Chip tone="blue" size="sm">Live usage tracker</Chip>
        <Chip tone="emerald" size="sm">Frame-by-frame analysis</Chip>
        <Chip tone="purple" size="sm">Download prompts as TXT</Chip>
      </div>

      <PageSection
        title="Today's signal"
        description="Monitor usage, see active jobs, and stay ahead of processing times without leaving the dashboard."
        icon={<Sparkles className="h-6 w-6" />}
        actions={
          <Button variant="ghost" size="sm" onClick={() => openTutorial('dashboard')}>
            Launch guided tour
          </Button>
        }
        variant="translucent"
      >
        <div className="grid gap-6 lg:grid-cols-[1.3fr,0.7fr]">
          <div className="grid gap-4 sm:grid-cols-2">
            {highlightCards.map((card) => (
              <Card
                key={card.key}
                variant="outline"
                padding="md"
                className="flex flex-col gap-3 bg-white/85 dark:bg-slate-900/70"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-500 dark:text-slate-400">{card.label}</span>
                  <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 dark:bg-indigo-500/10 dark:text-indigo-200">
                    {card.icon}
                  </span>
                </div>
                <p className="text-3xl font-semibold text-gray-900 dark:text-slate-100">{card.value}</p>
                <span className="text-xs uppercase tracking-wide text-gray-400 dark:text-slate-500">{card.helper}</span>
              </Card>
            ))}
          </div>
          <UsageStatus className="h-full" />
        </div>
      </PageSection>

      <div ref={uploadRef} />
      <PageSection
        title="Upload new analysis"
        description="Drop an image or motion clip. We keep you informed with snackbars while the pipeline runs."
        icon={<Upload className="h-6 w-6" />}
      >
        <UploadComponent
          onUpload={handleUpload}
          maxFileSize={100 * 1024 * 1024}
          acceptedTypes={['image/*', 'video/*']}
          disabled={false}
        />
        <div className="mt-6 grid gap-3 sm:grid-cols-3 text-sm text-gray-500 dark:text-slate-400">
          <div className="flex items-center gap-3 rounded-2xl border border-gray-200/60 bg-white/80 px-4 py-3 dark:border-slate-700/60 dark:bg-slate-900/70">
            <Film className="h-4 w-4 text-purple-500" />
            <span>Video up to 5 minutes · 100MB</span>
          </div>
          <div className="flex items-center gap-3 rounded-2xl border border-gray-200/60 bg-white/80 px-4 py-3 dark:border-slate-700/60 dark:bg-slate-900/70">
            <ImageIcon className="h-4 w-4 text-emerald-500" />
            <span>Images JPG, PNG, WEBP · transparency safe</span>
          </div>
          <div className="flex items-center gap-3 rounded-2xl border border-gray-200/60 bg-white/80 px-4 py-3 dark:border-slate-700/60 dark:bg-slate-900/70">
            <Clock className="h-4 w-4 text-blue-500" />
            <span>Average turnaround under 90 seconds</span>
          </div>
        </div>
      </PageSection>

      <PageSection
        title="Latest runs"
        description="Peek into the most recent analyses. Open any job to inspect the full prompt breakdown."
        icon={<History className="h-6 w-6" />}
        actions={
          <Button variant="outline" size="sm" onClick={() => navigate('/history')}>
            View all history
          </Button>
        }
      >
        {isLoadingHistory ? (
          <div className="flex items-center justify-center gap-3 rounded-3xl border border-dashed border-blue-300/70 bg-blue-50/40 p-10 text-blue-600 dark:border-indigo-500/40 dark:bg-indigo-500/10 dark:text-indigo-200">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Fetching your latest analyses…</span>
          </div>
        ) : recentAnalyses.length > 0 ? (
          <div className="space-y-4">
            {recentAnalyses.map((job) => {
              const status = statusConfig(job.status);
              const isVideo = job.content_type?.startsWith('video');

              return (
                <Card
                  key={job.job_id}
                  variant="outline"
                  padding="md"
                  interactive
                  className="bg-white/85 dark:bg-slate-900/70"
                >
                  <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
                    <div className="flex flex-1 gap-4">
                      <div className="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-2xl border border-white/60 bg-gradient-to-br from-blue-100 via-white to-purple-100 shadow-inner shadow-blue-100 dark:border-white/10 dark:from-slate-800 dark:via-slate-900 dark:to-slate-800">
                        {job.thumbnail_url ? (
                          <img
                            src={job.thumbnail_url}
                            alt={job.filename}
                            className="h-full w-full object-cover"
                            onError={(event) => {
                              const target = event.currentTarget as HTMLImageElement;
                              target.style.display = 'none';
                            }}
                          />
                        ) : (
                          <span className="text-2xl">{isVideo ? '🎬' : '🖼️'}</span>
                        )}
                      </div>

                      <div className="flex-1 space-y-4">
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-slate-100">{job.filename}</h3>
                            <p className="text-sm text-gray-500 dark:text-slate-400">Created {formatDate(job.created_at)}</p>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            <Chip tone={status.tone} size="sm">
                              {status.label}
                            </Chip>
                            <Chip tone={isVideo ? 'purple' : 'blue'} size="sm">
                              {isVideo ? 'Video asset' : 'Image asset'}
                            </Chip>
                            {job.summary?.resolution && (
                              <Chip tone="gray" size="sm">{job.summary.resolution}</Chip>
                            )}
                          </div>
                        </div>

                        {job.prompt_preview && (
                          <p className="line-clamp-2 rounded-2xl border border-gray-200/60 bg-white/70 p-4 text-sm text-gray-700 shadow-inner shadow-gray-200/40 dark:border-slate-700/60 dark:bg-slate-900/60 dark:text-slate-200">
                            {job.prompt_preview}
                          </p>
                        )}

                        <div className="flex flex-wrap gap-2 text-xs text-gray-500 dark:text-slate-400">
                          <span>Processing time: {formatProcessingTime(job.processing_time_seconds)}</span>
                          {job.summary?.analysis_method && <span>Method: {job.summary.analysis_method}</span>}
                          {job.summary?.fps && <span>FPS: {job.summary.fps}</span>}
                        </div>

                        {job.enhancement_features && job.enhancement_features.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {job.enhancement_features.slice(0, 4).map((feature: string) => (
                              <Chip key={feature} tone="purple" size="sm">
                                {feature}
                              </Chip>
                            ))}
                            {job.enhancement_features.length > 4 && (
                              <Chip tone="gray" size="sm">
                                +{job.enhancement_features.length - 4} more
                              </Chip>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-col items-stretch gap-3 lg:w-48">
                      <Button
                        size="sm"
                        onClick={() => handleViewJob(job)}
                        leadingIcon={<Eye className="h-4 w-4" />}
                      >
                        View details
                      </Button>

                      {job.main_prompt && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopyPrompt(job.main_prompt!, job.job_id)}
                          leadingIcon={
                            copiedPrompt === job.job_id ? (
                              <Check className="h-4 w-4" />
                            ) : (
                              <Copy className="h-4 w-4" />
                            )
                          }
                        >
                          {copiedPrompt === job.job_id ? 'Copied' : 'Copy prompt'}
                        </Button>
                      )}

                      {job.main_prompt && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownloadPrompt(job)}
                          leadingIcon={<Download className="h-4 w-4" />}
                        >
                          Download TXT
                        </Button>
                      )}

                      {job.status === 'processing' && (
                        <div className="flex items-center justify-center gap-2 rounded-2xl border border-amber-200/60 bg-amber-50/70 px-3 py-2 text-xs font-medium text-amber-700 dark:border-amber-400/20 dark:bg-amber-500/10 dark:text-amber-200">
                          <Loader2 className="h-3.5 w-3.5 animate-spin" />
                          <span>Processing…</span>
                        </div>
                      )}
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center gap-4 rounded-3xl border border-dashed border-gray-300/70 bg-white/70 p-12 text-center text-gray-500 dark:border-slate-600/70 dark:bg-slate-900/60 dark:text-slate-300">
            <span className="text-4xl">🎬</span>
            <div>
              <p className="text-lg font-semibold">No analysis jobs yet</p>
              <p className="text-sm">Upload your first asset to see the full prompt breakdown here.</p>
            </div>
            <Button onClick={() => uploadRef.current?.scrollIntoView({ behavior: 'smooth' })}>Start an analysis</Button>
          </div>
        )}
      </PageSection>

      {activeJobId && activeJobInfo && (
        <ProgressModal
          jobId={activeJobId}
          filename={activeJobInfo.filename}
          contentType={activeJobInfo.contentType}
          isOpen={Boolean(activeJobId)}
          onClose={() => {
            setActiveJobId(null);
            setActiveJobInfo(null);
          }}
          onComplete={handleJobComplete}
        />
      )}

      {selectedJob && (
        <JobResultModal
          isOpen={showJobModal}
          onClose={() => {
            setShowJobModal(false);
            setSelectedJob(null);
          }}
          job={selectedJob}
        />
      )}
    </PageContainer>
  );
};

export default DashboardPage;
