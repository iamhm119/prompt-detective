import React from 'react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface ChipProps extends React.HTMLAttributes<HTMLSpanElement> {
  tone?: 'blue' | 'purple' | 'emerald' | 'amber' | 'gray' | 'rose';
  size?: 'sm' | 'md';
  leadingIcon?: React.ReactNode;
  trailingIcon?: React.ReactNode;
  pill?: boolean;
}

const toneStyles: Record<NonNullable<ChipProps['tone']>, string> = {
  blue: 'bg-blue-50 text-blue-700 border border-blue-100 dark:bg-indigo-500/15 dark:text-indigo-200 dark:border-indigo-400/30',
  purple: 'bg-purple-50 text-purple-700 border border-purple-100 dark:bg-purple-500/15 dark:text-purple-200 dark:border-purple-400/30',
  emerald: 'bg-emerald-50 text-emerald-700 border border-emerald-100 dark:bg-emerald-500/15 dark:text-emerald-200 dark:border-emerald-400/30',
  amber: 'bg-amber-50 text-amber-700 border border-amber-100 dark:bg-amber-500/10 dark:text-amber-200 dark:border-amber-400/30',
  gray: 'bg-gray-100 text-gray-700 border border-gray-200 dark:bg-slate-800/80 dark:text-slate-200 dark:border-slate-600/70',
  rose: 'bg-rose-50 text-rose-700 border border-rose-100 dark:bg-rose-500/15 dark:text-rose-200 dark:border-rose-400/30',
};

const sizeStyles: Record<NonNullable<ChipProps['size']>, string> = {
  sm: 'text-xs px-2.5 py-1 gap-1',
  md: 'text-sm px-3 py-1.5 gap-1.5',
};

const Chip: React.FC<ChipProps> = ({
  className,
  tone = 'blue',
  size = 'md',
  leadingIcon,
  trailingIcon,
  pill = true,
  children,
  ...props
}) => {
  return (
    <span
      className={twMerge(
        'inline-flex items-center font-medium',
        toneStyles[tone],
        sizeStyles[size],
        pill ? 'rounded-full' : 'rounded-lg',
        className
      )}
      {...props}
    >
      {leadingIcon && <span className={clsx('flex items-center justify-center text-current')}>{leadingIcon}</span>}
      <span>{children}</span>
      {trailingIcon && <span className={clsx('flex items-center justify-center text-current')}>{trailingIcon}</span>}
    </span>
  );
};

export default Chip;
