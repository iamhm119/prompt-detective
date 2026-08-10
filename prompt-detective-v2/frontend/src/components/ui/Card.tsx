import React from 'react';
import { twMerge } from 'tailwind-merge';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'elevated' | 'outline' | 'translucent';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  interactive?: boolean;
}

const paddingMap: Record<NonNullable<CardProps['padding']>, string> = {
  none: 'p-0',
  sm: 'p-4 sm:p-6',
  md: 'p-6 sm:p-8',
  lg: 'p-8 sm:p-10',
};

const variantMap: Record<NonNullable<CardProps['variant']>, string> = {
  elevated:
    'bg-white/90 backdrop-blur-xl shadow-[0_20px_45px_-20px_rgba(79,70,229,0.45)] border border-white/60 dark:bg-slate-900/80 dark:border-white/5 dark:shadow-[0_20px_45px_-20px_rgba(15,23,42,0.65)]',
  outline:
    'bg-white/80 border border-gray-200/70 shadow-[0_12px_30px_-12px_rgba(99,102,241,0.25)] backdrop-blur-md dark:bg-slate-900/70 dark:border-slate-700/70 dark:shadow-[0_12px_30px_-12px_rgba(15,23,42,0.6)]',
  translucent:
    'bg-gradient-to-br from-white/60 via-white/30 to-white/10 border border-white/40 backdrop-blur-2xl shadow-[0_18px_50px_-15px_rgba(56,189,248,0.35)] dark:from-slate-900/70 dark:via-slate-900/40 dark:to-slate-900/10 dark:border-white/5 dark:shadow-[0_18px_50px_-15px_rgba(15,23,42,0.65)]',
};

const Card: React.FC<CardProps> = ({
  variant = 'elevated',
  padding = 'md',
  interactive = false,
  className,
  children,
  ...props
}) => {
  return (
    <div
      className={twMerge(
        'group relative overflow-hidden rounded-3xl transition-all duration-400 ease-out',
        variantMap[variant],
        paddingMap[padding],
        interactive && 'hover:-translate-y-1 hover:shadow-[0_30px_70px_-25px_rgba(79,70,229,0.4)]',
        className
      )}
      {...props}
    >
      {/* sheen */}
      <span className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-500 group-hover:opacity-100">
        <span className="absolute -top-1/2 left-1/2 h-[200%] w-[200%] -translate-x-1/2 rotate-45 bg-gradient-to-tr from-transparent via-white/40 to-transparent" />
      </span>
      {children}
    </div>
  );
};

export default Card;
