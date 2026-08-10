import React, { useEffect, useMemo, useState } from 'react';
import {
  Calendar,
  Check,
  Clock,
  Copy,
  Download,
  Eye,
  FileImage,
  FileVideo,
  Filter,
  Loader2,
  Search,
  Sparkles,
  TrendingUp,
  X,
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useUpload } from '../hooks/useUpload';
import PageContainer from '../components/page/PageContainer';
import PageHeader from '../components/PageHeader';
import PageSection from '../components/page/PageSection';
import Card from '../components/ui/Card';
import Chip from '../components/ui/Chip';
import { Button } from '../components/ui/Button';

interface UsageHistoryItem {
  job_id: string;
  filename: string;
  content_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  main_prompt?: string;
  prompt_preview?: string;
  summary?: {
    resolution?: string;
    duration?: number;
    frames_analyzed?: number;
    analysis_method?: string;
    enhancement_features?: string[];
  };
  enhancement_features?: string[];
  created_at: string;
  completed_at?: string;
  processing_time_seconds?: number;
  thumbnail_url?: string;
}

type HistoryFilter = 'all' | 'image' | 'video' | 'completed' | 'failed';

const formatDate = (value: string) =>
  new Date(value).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });

const formatDuration = (seconds?: number) => {
  if (!seconds) return '—';
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds % 60;
  return `${minutes}m ${remainder}s`;
};

const historyFilters: { label: string; value: HistoryFilter }[] = [
  { label: 'All items', value: 'all' },
  { label: 'Images', value: 'image' },
  { label: 'Videos', value: 'video' },
  { label: 'Completed', value: 'completed' },
  { label: 'Failed', value: 'failed' },
];

const UsageHistoryPage: React.FC = () => {
  const { user } = useAuth();
  const { listJobs } = useUpload();
  const [items, setItems] = useState<UsageHistoryItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<UsageHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState<HistoryFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedItem, setSelectedItem] = useState<UsageHistoryItem | null>(null);
  const [brokenThumbnails, setBrokenThumbnails] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setIsLoading(true);
        const response = await listJobs('', 60, 0);
        setItems(response.jobs || []);
      } catch (error) {
        console.error('Failed to load usage history:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHistory();
  }, [listJobs]);

  useEffect(() => {
    let next = [...items];

    if (selectedFilter === 'image' || selectedFilter === 'video') {
      next = next.filter((item) => item.content_type?.startsWith(selectedFilter));
    } else if (selectedFilter === 'completed' || selectedFilter === 'failed') {
      next = next.filter((item) => item.status === selectedFilter);
    }

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      next = next.filter(
        (item) =>
          item.filename.toLowerCase().includes(query) ||
          item.main_prompt?.toLowerCase().includes(query) ||
          item.prompt_preview?.toLowerCase().includes(query)
      );
    }

    setFilteredItems(next);
  }, [items, selectedFilter, searchQuery]);

  const stats = useMemo(() => {
    const total = items.length;
    const completed = items.filter((item) => item.status === 'completed').length;
    const videos = items.filter((item) => item.content_type?.startsWith('video')).length;
    const images = items.filter((item) => item.content_type?.startsWith('image')).length;

    return {
      total,
      completed,
      videos,
      images,
    };
  }, [items]);

  const statCards = useMemo(
    () => [
      {
        key: 'total',
        label: 'Total analyses',
        value: stats.total,
        helper: 'All uploads in scope',
        icon: <TrendingUp className="h-5 w-5 text-indigo-500" />,
      },
      {
        key: 'completed',
        label: 'Completed jobs',
        value: stats.completed,
        helper: 'Ready for export',
        icon: <Sparkles className="h-5 w-5 text-emerald-500" />,
      },
      {
        key: 'videos',
        label: 'Video assets',
        value: stats.videos,
        helper: 'Motion analyses',
        icon: <FileVideo className="h-5 w-5 text-blue-500" />,
      },
      {
        key: 'images',
        label: 'Image assets',
        value: stats.images,
        helper: 'Still references',
        icon: <FileImage className="h-5 w-5 text-purple-500" />,
      },
    ],
    [stats]
  );

  const applyCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (error) {
      console.error('Copy failed:', error);
    }
  };

  const getStatusTone = (status: UsageHistoryItem['status']) => {
    switch (status) {
      case 'completed':
        return { tone: 'emerald' as const, label: 'Completed' };
      case 'processing':
        return { tone: 'amber' as const, label: 'Processing' };
      case 'pending':
        return { tone: 'blue' as const, label: 'Queued' };
      case 'failed':
        return { tone: 'rose' as const, label: 'Failed' };
      default:
        return { tone: 'gray' as const, label: 'Unknown' };
    }
  };

  return (
    <PageContainer>
      <PageHeader
        title="Usage history"
        subtitle="Every analysis you run is archived with prompt previews, enhancement markers, and export-ready metadata."
        breadcrumbs={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'History' }]}
        primaryAction={{ label: 'Upload new asset', onClick: () => window.scrollTo({ top: 0, behavior: 'smooth' }) }}
        secondaryAction={{ label: 'Export CSV', onClick: () => console.log('Export history requested') }}
        illustration={<HistorySpark />}
      />

      <div className="flex flex-wrap gap-3 text-sm text-gray-500 dark:text-slate-400">
        <Chip tone="blue" size="sm">Live filters</Chip>
        <Chip tone="emerald" size="sm">Prompt previews</Chip>
        <Chip tone="purple" size="sm">Enhancement markers</Chip>
      </div>

      <PageSection
        title="Snapshot"
        description="Monitor how usage trends across formats and quickly spot the outcome distribution."
        icon={<TrendingUp className="h-6 w-6" />}
        variant="translucent"
      >
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {statCards.map((stat) => (
            <Card
              key={stat.key}
              variant="outline"
              padding="md"
              className="flex flex-col gap-3 bg-white/85 dark:bg-slate-900/70"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-500 dark:text-slate-400">{stat.label}</span>
                <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 dark:bg-indigo-500/10 dark:text-indigo-200">
                  {stat.icon}
                </span>
              </div>
              <p className="text-3xl font-semibold text-gray-900 dark:text-slate-100">{stat.value}</p>
              <span className="text-xs uppercase tracking-wide text-gray-400 dark:text-slate-500">{stat.helper}</span>
            </Card>
          ))}
        </div>
      </PageSection>

      <PageSection
        title="Filter & search"
        description="Use smart filters or search across filenames, captured prompts, and annotations."
        icon={<Filter className="h-6 w-6" />}
      >
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="relative w-full max-w-lg">
            <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Search filename, prompt keywords, or enhancements"
              className="w-full rounded-full border border-gray-200 bg-white/90 px-12 py-3 text-sm text-gray-700 shadow-[0_10px_30px_-20px_rgba(59,130,246,0.4)] focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-900/70 dark:text-slate-200"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            {historyFilters.map((filter) => (
              <Button
                key={filter.value}
                variant={selectedFilter === filter.value ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setSelectedFilter(filter.value)}
              >
                {filter.label}
              </Button>
            ))}
          </div>
        </div>
      </PageSection>

      <PageSection
        title="Archive"
        description="Click into any record to open the full prompt, enhancement notes, and export options."
        icon={<Sparkles className="h-6 w-6" />}
      >
        {isLoading ? (
          <div className="flex items-center justify-center gap-3 rounded-3xl border border-dashed border-blue-300/70 bg-blue-50/40 p-10 text-blue-600 dark:border-indigo-500/40 dark:bg-indigo-500/10 dark:text-indigo-200">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Loading your archive…</span>
          </div>
        ) : filteredItems.length === 0 ? (
          <Card variant="outline" padding="lg" className="text-center text-gray-500 dark:text-slate-300">
            <FileImage className="mx-auto h-12 w-12 text-gray-300 dark:text-slate-600" />
            <p className="mt-4 text-lg font-semibold text-gray-800 dark:text-slate-100">No results matched</p>
            <p className="text-sm">Adjust filters or run a fresh analysis to populate your archive.</p>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {filteredItems.map((item) => {
              const isVideo = item.content_type?.startsWith('video');
              const status = getStatusTone(item.status);
              const thumbnailUrl = item.thumbnail_url;
              const showThumbnail = Boolean(thumbnailUrl && !brokenThumbnails[item.job_id]);

              return (
                  <Card
                  key={item.job_id}
                  variant="outline"
                  padding="md"
                  interactive
                  className="group flex h-full flex-col gap-4 bg-white/85 dark:bg-slate-900/70"
                  onClick={() => setSelectedItem(item)}
                >
                  <div className="overflow-hidden rounded-3xl border border-white/40 bg-gradient-to-br from-blue-100 via-white to-purple-100 shadow-inner shadow-blue-100 dark:border-slate-700/60 dark:from-slate-900/40 dark:via-slate-900/20 dark:to-slate-900/40">
                    {showThumbnail ? (
                      <div className="relative h-44 w-full">
                        <img
                          src={thumbnailUrl}
                          alt={`${item.filename} thumbnail`}
                          loading="lazy"
                          className="h-full w-full object-cover transition duration-500 group-hover:scale-[1.04]"
                          onError={() =>
                            setBrokenThumbnails((prev) => ({
                              ...prev,
                              [item.job_id]: true,
                            }))
                          }
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/45 via-black/5 to-transparent" />
                        <div className="absolute bottom-3 left-3 flex items-center gap-2">
                          <Chip tone={status.tone} size="sm" className="backdrop-blur">
                            {status.label}
                          </Chip>
                          <Chip tone={isVideo ? 'purple' : 'blue'} size="sm" className="backdrop-blur">
                            {isVideo ? 'Video asset' : 'Image asset'}
                          </Chip>
                        </div>
                      </div>
                    ) : (
                      <div className="flex h-44 w-full flex-col items-center justify-center gap-3 bg-gradient-to-br from-blue-200 via-white to-purple-200 dark:from-slate-900/60 dark:via-slate-900/30 dark:to-slate-900/60">
                        <span className="text-3xl">{isVideo ? '🎬' : '🖼️'}</span>
                        <p className="text-xs font-medium text-gray-500 dark:text-slate-400">Preview not available</p>
                      </div>
                    )}
                  </div>

                  <div className="flex items-start justify-between">
                    <div className="space-y-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-slate-100">{item.filename}</h3>
                      <p className="text-xs text-gray-500 dark:text-slate-400">Created {formatDate(item.created_at)}</p>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      {item.summary?.resolution && <Chip tone="gray" size="sm">{item.summary.resolution}</Chip>}
                    </div>
                  </div>

                  {item.prompt_preview && (
                    <p className="line-clamp-3 rounded-2xl border border-gray-200/60 bg-white/70 p-4 text-sm text-gray-700 shadow-inner shadow-gray-200/40 dark:border-slate-700/60 dark:bg-slate-900/60 dark:text-slate-200">
                      {item.prompt_preview}
                    </p>
                  )}

                  <div className="flex flex-wrap gap-2 text-xs text-gray-500 dark:text-slate-400">
                    <span>Processing: {formatDuration(item.processing_time_seconds)}</span>
                    {item.summary?.analysis_method && <span>Method: {item.summary.analysis_method}</span>}
                    {item.summary?.frames_analyzed && <span>Frames: {item.summary.frames_analyzed}</span>}
                  </div>

                  {item.enhancement_features && item.enhancement_features.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {item.enhancement_features.slice(0, 3).map((feature: string) => (
                        <Chip key={feature} tone="purple" size="sm">
                          {feature.replace(/_/g, ' ')}
                        </Chip>
                      ))}
                      {item.enhancement_features.length > 3 && (
                        <Chip tone="gray" size="sm">+{item.enhancement_features.length - 3} more</Chip>
                      )}
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-2 text-xs text-gray-500 dark:text-slate-400">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-3.5 w-3.5" />
                      <span>{formatDate(item.created_at)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-3.5 w-3.5" />
                      <span>{formatDuration(item.processing_time_seconds)}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2 pt-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      leadingIcon={<Eye className="h-4 w-4" />}
                      onClick={(event) => {
                        event.stopPropagation();
                        setSelectedItem(item);
                      }}
                    >
                      View details
                    </Button>
                    {item.main_prompt && (
                      <Button
                        size="sm"
                        variant="outline"
                        leadingIcon={<Copy className="h-4 w-4" />}
                        onClick={(event) => {
                          event.stopPropagation();
                          applyCopy(item.main_prompt!);
                        }}
                      >
                        Copy prompt
                      </Button>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </PageSection>

      {selectedItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <Card variant="elevated" padding="lg" className="relative w-full max-w-4xl overflow-y-auto max-h-[92vh]">
            <button
              type="button"
              onClick={() => setSelectedItem(null)}
              className="absolute right-6 top-6 text-gray-400 transition hover:text-gray-600 dark:text-slate-500 dark:hover:text-slate-200"
            >
              <X className="h-5 w-5" />
            </button>

            <div className="pr-8">
              <div className="mb-6 space-y-2">
                <Chip tone="blue" size="sm">Job ID: {selectedItem.job_id}</Chip>
                <h2 className="text-2xl font-semibold text-gray-900 dark:text-slate-100">{selectedItem.filename}</h2>
                <p className="text-sm text-gray-500 dark:text-slate-400">Completed {selectedItem.completed_at ? formatDate(selectedItem.completed_at) : 'processing'}</p>
              </div>

              <div className="mb-8 overflow-hidden rounded-3xl border border-gray-200/70 bg-gray-100 shadow-inner shadow-gray-200/50 dark:border-slate-700/60 dark:bg-slate-900/60">
                {selectedItem.thumbnail_url && !brokenThumbnails[selectedItem.job_id] ? (
                  <img
                    src={selectedItem.thumbnail_url}
                    alt={`${selectedItem.filename} analysis preview`}
                    className="h-80 w-full object-cover"
                    onError={() =>
                      setBrokenThumbnails((prev) => ({
                        ...prev,
                        [selectedItem.job_id]: true,
                      }))
                    }
                  />
                ) : (
                  <div className="flex h-80 items-center justify-center bg-gradient-to-br from-blue-200 via-white to-purple-200 text-5xl dark:from-slate-900/60 dark:via-slate-900/30 dark:to-slate-900/60">
                    {selectedItem.content_type?.startsWith('video') ? '🎬' : '🖼️'}
                  </div>
                )}
              </div>

              {selectedItem.main_prompt && (
                <div className="mb-6 space-y-3">
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-slate-100">Generated prompt</h3>
                  <div className="rounded-3xl border border-gray-200/60 bg-white/70 p-5 text-sm leading-relaxed text-gray-800 shadow-inner shadow-gray-200/40 dark:border-slate-700/60 dark:bg-slate-900/60 dark:text-slate-200">
                    {selectedItem.main_prompt}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      variant="primary"
                      size="sm"
                      leadingIcon={<Copy className="h-4 w-4" />}
                      onClick={() => applyCopy(selectedItem.main_prompt!)}
                    >
                      Copy prompt
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      leadingIcon={<Download className="h-4 w-4" />}
                      onClick={() => console.log('Download prompt requested')}
                    >
                      Download TXT
                    </Button>
                  </div>
                </div>
              )}

              {selectedItem.enhancement_features && selectedItem.enhancement_features.length > 0 && (
                <div className="mt-6 space-y-3">
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-slate-100">Enhancement features</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedItem.enhancement_features.map((feature: string) => (
                      <Chip key={feature} tone="purple" size="sm">
                        {feature.replace(/_/g, ' ')}
                      </Chip>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>
      )}
    </PageContainer>
  );
};

const HistorySpark = () => (
  <span className="flex h-14 w-14 items-center justify-center rounded-3xl bg-white/70 text-indigo-500 shadow-inner shadow-blue-100 backdrop-blur-xl dark:bg-slate-900/60 dark:text-indigo-200 dark:shadow-slate-900/40">
    <Sparkles className="h-7 w-7" />
  </span>
);

export default UsageHistoryPage;
