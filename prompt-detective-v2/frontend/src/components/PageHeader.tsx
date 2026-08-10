import React from 'react';
import Breadcrumbs, { BreadcrumbItem } from './ui/Breadcrumbs';
import { Button } from './ui/Button';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: BreadcrumbItem[];
  primaryAction?: {
    label: string;
    onClick: () => void;
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
  illustration?: React.ReactNode;
}

const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  breadcrumbs,
  primaryAction,
  secondaryAction,
  illustration,
}) => {
  return (
  <div className="relative overflow-hidden rounded-[32px] border border-white/50 bg-gradient-to-br from-blue-600/10 via-white/70 to-purple-600/10 p-8 shadow-[0_30px_85px_-45px_rgba(59,130,246,0.55)] dark:border-white/10 dark:from-indigo-500/20 dark:via-slate-900/70 dark:to-purple-500/10 dark:shadow-[0_30px_85px_-45px_rgba(15,23,42,0.75)]">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.25),_transparent_55%)] dark:bg-[radial-gradient(circle_at_top,_rgba(129,140,248,0.18),_transparent_55%)]" />
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div>
          {breadcrumbs && <Breadcrumbs items={breadcrumbs} className="mb-4" />}
          <h1 className="text-3xl font-bold text-gray-900 sm:text-4xl md:text-5xl dark:text-white">{title}</h1>
          {subtitle && <p className="mt-3 max-w-2xl text-base text-gray-600 sm:text-lg dark:text-white/80">{subtitle}</p>}
          <div className="mt-6 flex flex-wrap gap-3">
            {primaryAction && (
              <Button size="lg" onClick={primaryAction.onClick}>
                {primaryAction.label}
              </Button>
            )}
            {secondaryAction && (
              <Button variant="outline" size="lg" onClick={secondaryAction.onClick}>
                {secondaryAction.label}
              </Button>
            )}
          </div>
        </div>
        {illustration && (
          <div className="flex shrink-0 items-center justify-center md:w-56">
            <div className="h-32 w-32 rounded-3xl bg-white/60 p-6 shadow-inner shadow-blue-100 backdrop-blur-xl dark:bg-slate-900/60 dark:shadow-slate-900/40">
              {illustration}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PageHeader;
