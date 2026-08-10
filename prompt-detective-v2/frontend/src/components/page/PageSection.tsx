import React from 'react';
import Card, { CardProps } from '../ui/Card';
import clsx from 'clsx';

interface PageSectionProps extends Omit<CardProps, 'children'> {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  actions?: React.ReactNode;
  children?: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
}

const PageSection: React.FC<PageSectionProps> = ({
  title,
  description,
  icon,
  actions,
  children,
  footer,
  className,
  variant = 'elevated',
  padding = 'lg',
  ...props
}) => {
  const hasHeader = Boolean(title || description || icon || actions);

  return (
    <Card
      variant={variant}
      padding={padding}
      className={clsx('space-y-6', className)}
      {...props}
    >
      {hasHeader && (
        <header className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div className="flex gap-4">
            {icon && (
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/70 text-blue-600 shadow-inner shadow-blue-100 dark:bg-slate-900/60 dark:text-indigo-200 dark:shadow-slate-900/40">
                {icon}
              </div>
            )}
            <div>
              {title && <h2 className="text-2xl font-semibold text-gray-900 dark:text-slate-50">{title}</h2>}
              {description && <p className="mt-2 text-sm text-gray-500 dark:text-slate-300">{description}</p>}
            </div>
          </div>
          {actions && <div className="flex shrink-0 items-center gap-3">{actions}</div>}
        </header>
      )}

      {children}

      {footer && <footer>{footer}</footer>}
    </Card>
  );
};

export default PageSection;
