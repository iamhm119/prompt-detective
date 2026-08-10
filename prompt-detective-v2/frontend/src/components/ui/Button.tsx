import React from 'react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

type ButtonElement = HTMLButtonElement | HTMLAnchorElement;

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  href?: string;
  to?: string;
  component?: React.ElementType;
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  isLoading?: boolean;
  leadingIcon?: React.ReactNode;
  trailingIcon?: React.ReactNode;
}

export const Button = React.forwardRef<ButtonElement, ButtonProps>(
  (
    {
      children,
      className,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
      isLoading = false,
      leadingIcon,
      trailingIcon,
  href,
  to,
      component,
      disabled,
      ...props
    },
    ref
  ) => {
    const Comp = component || (href ? 'a' : 'button');
    const isDisabled = disabled || isLoading;

    const baseClasses = 'relative inline-flex items-center justify-center gap-2 rounded-full font-semibold transition-all duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-400 disabled:cursor-not-allowed disabled:opacity-50 dark:focus-visible:ring-offset-slate-900';

    const variantClasses: Record<ButtonVariant, string> = {
      primary:
        'bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-200 hover:shadow-xl hover:-translate-y-0.5 focus-visible:ring-offset-0 dark:shadow-indigo-900/40',
      secondary:
        'bg-white text-gray-900 border border-gray-200 hover:border-gray-300 hover:bg-gray-50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] focus-visible:ring-blue-200 dark:bg-slate-900/80 dark:text-slate-100 dark:border-slate-700 dark:hover:border-slate-500 dark:hover:bg-slate-800/80 dark:shadow-[0_8px_30px_rgba(15,23,42,0.35)]',
      outline:
        'border border-blue-500/40 text-blue-600 bg-white/80 hover:bg-blue-50 shadow-sm shadow-blue-100 focus-visible:ring-blue-200 dark:border-indigo-400/40 dark:text-indigo-200 dark:bg-slate-900/60 dark:hover:bg-slate-900',
      ghost:
        'bg-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-100/60 focus-visible:ring-gray-200 dark:text-slate-300 dark:hover:text-white dark:hover:bg-slate-800/70 dark:focus-visible:ring-slate-700',
      destructive:
        'bg-gradient-to-r from-red-500 to-pink-500 text-white shadow-lg shadow-red-200 hover:shadow-xl hover:-translate-y-0.5 focus-visible:ring-red-200 focus-visible:ring-offset-0 dark:shadow-red-950/40',
    };

    const sizeClasses: Record<ButtonSize, string> = {
      xs: 'text-xs px-3 py-1.5',
      sm: 'text-sm px-3.5 py-2',
      md: 'text-sm px-4 py-2.5',
      lg: 'text-base px-5 py-3',
      xl: 'text-base px-6 py-3.5',
    };

    const mergedClassName = twMerge(
      baseClasses,
      variantClasses[variant],
      sizeClasses[size],
      fullWidth ? 'w-full' : '',
      className
    );

    return (
      <Comp
        ref={ref as any}
        className={mergedClassName}
  href={href}
  to={to}
        disabled={Comp === 'button' ? isDisabled : undefined}
        {...props}
      >
        {leadingIcon && (
          <span className={clsx('flex items-center justify-center', isLoading && 'opacity-0')}>
            {leadingIcon}
          </span>
        )}
        <span className={clsx('flex items-center gap-1', isLoading && 'opacity-0')}>{children}</span>
        {trailingIcon && (
          <span className={clsx('flex items-center justify-center', isLoading && 'opacity-0')}>
            {trailingIcon}
          </span>
        )}
        {isLoading && (
          <span className="absolute inset-0 flex items-center justify-center">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/70 border-t-transparent"></span>
          </span>
        )}
      </Comp>
    );
  }
);

Button.displayName = 'Button';

export default Button;
