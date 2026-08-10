import React from 'react';
import { Link } from 'react-router-dom';
import clsx from 'clsx';

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  className?: string;
}

const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items, className }) => {
  if (!items?.length) return null;

  return (
    <nav className={clsx('flex items-center text-sm text-gray-500 dark:text-white/75', className)} aria-label="Breadcrumb">
      <ol className="flex items-center space-x-2">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <li key={`${item.label}-${index}`} className="flex items-center">
              {item.href && !isLast ? (
                <Link
                  to={item.href}
                  className="rounded-full bg-white/70 px-3 py-1 font-medium text-blue-600 shadow-sm shadow-blue-100 transition hover:bg-blue-50 hover:text-blue-700 dark:bg-slate-900/70 dark:text-white/85 dark:shadow-slate-900/40 dark:hover:bg-slate-800"
                >
                  {item.label}
                </Link>
              ) : (
                <span className="rounded-full bg-blue-600/10 px-3 py-1 font-semibold text-blue-700 dark:bg-indigo-500/20 dark:text-white">
                  {item.label}
                </span>
              )}
              {!isLast && <span className="mx-2 text-gray-300 dark:text-white/60">/</span>}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;
