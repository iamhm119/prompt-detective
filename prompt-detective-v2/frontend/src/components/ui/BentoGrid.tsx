import React from 'react';
import clsx from 'clsx';

export interface BentoItem {
  key: string;
  title: string;
  description: string;
  icon?: React.ReactNode;
  footer?: React.ReactNode;
  accent?: 'blue' | 'purple' | 'amber' | 'emerald';
}

export interface BentoGridProps {
  items: BentoItem[];
  className?: string;
}

const accentMap: Record<NonNullable<BentoItem['accent']>, string> = {
  blue: 'from-blue-500/15 to-blue-500/5 border-blue-500/20 dark:from-indigo-500/25 dark:via-indigo-500/10 dark:to-slate-900/70 dark:border-indigo-400/30',
  purple: 'from-purple-500/15 to-purple-500/5 border-purple-500/20 dark:from-violet-500/25 dark:via-violet-500/10 dark:to-slate-900/70 dark:border-violet-400/30',
  amber: 'from-amber-500/15 to-amber-500/5 border-amber-500/20 dark:from-amber-500/25 dark:via-amber-500/10 dark:to-slate-900/70 dark:border-amber-400/30',
  emerald: 'from-emerald-500/15 to-emerald-500/5 border-emerald-500/20 dark:from-emerald-500/25 dark:via-emerald-500/10 dark:to-slate-900/70 dark:border-emerald-400/30',
};

const BentoGrid: React.FC<BentoGridProps> = ({ items, className }) => {
  return (
    <div className={clsx('grid gap-6 md:grid-cols-2 xl:grid-cols-4', className)}>
      {items.map((item) => (
        <div
          key={item.key}
          className={clsx(
            'group relative overflow-hidden rounded-[28px] border bg-gradient-to-br p-6 shadow-[0_22px_60px_-32px_rgba(79,70,229,0.55)] backdrop-blur-xl transition-all duration-500 hover:-translate-y-1 hover:shadow-[0_30px_90px_-45px_rgba(99,102,241,0.55)] dark:shadow-[0_30px_90px_-55px_rgba(15,23,42,0.8)]',
            item.accent
              ? accentMap[item.accent]
              : 'from-gray-200/20 to-white/50 border-white/40 dark:from-slate-900/85 dark:via-slate-900/70 dark:to-slate-900/60 dark:border-white/10'
          )}
        >
          <div className="relative z-10">
            {item.icon && (
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-white/80 text-2xl shadow-lg shadow-white/40 dark:bg-slate-900/60 dark:text-white dark:shadow-indigo-950/40">
                {item.icon}
              </div>
            )}
            <h3 className="text-lg font-semibold text-gray-900 sm:text-xl dark:text-white">{item.title}</h3>
            <p className="mt-3 text-sm text-gray-600 sm:text-base dark:text-white/80">{item.description}</p>
            {item.footer && <div className="mt-4 text-sm font-medium text-blue-600 dark:text-indigo-200">{item.footer}</div>}
          </div>

          <span className="pointer-events-none absolute inset-0 bg-gradient-to-tr from-transparent via-white/20 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100 dark:via-white/5" />
        </div>
      ))}
    </div>
  );
};

export default BentoGrid;
