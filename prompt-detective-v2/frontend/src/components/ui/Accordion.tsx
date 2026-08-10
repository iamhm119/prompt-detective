import React, { useState } from 'react';
import clsx from 'clsx';
import { ChevronDown } from 'lucide-react';

export interface AccordionItem {
  id: string;
  title: string;
  description: React.ReactNode;
  helperText?: string;
}

export interface AccordionProps {
  items: AccordionItem[];
  defaultOpenId?: string;
  allowMultiple?: boolean;
  className?: string;
}

const Accordion: React.FC<AccordionProps> = ({
  items,
  defaultOpenId,
  allowMultiple = false,
  className,
}) => {
  const [openItems, setOpenItems] = useState<string[]>(defaultOpenId ? [defaultOpenId] : []);

  const handleToggle = (id: string) => {
    setOpenItems((prev) => {
      const isOpen = prev.includes(id);
      if (allowMultiple) {
        if (isOpen) {
          return prev.filter((item) => item !== id);
        }
        return [...prev, id];
      }
      return isOpen ? [] : [id];
    });
  };

  return (
    <div className={clsx('space-y-4', className)}>
      {items.map((item) => {
        const isOpen = openItems.includes(item.id);
        return (
          <div
            key={item.id}
            className={clsx(
              'overflow-hidden rounded-2xl border border-white/60 bg-white/80 shadow-[0_18px_60px_-30px_rgba(37,99,235,0.55)] transition-all duration-300 backdrop-blur-lg dark:border-white/8 dark:bg-slate-900/80 dark:shadow-[0_22px_70px_-35px_rgba(15,23,42,0.75)]',
              isOpen ? 'ring-1 ring-blue-100 dark:ring-indigo-400/40' : 'hover:-translate-y-0.5 hover:shadow-[0_30px_70px_-35px_rgba(79,70,229,0.45)] dark:hover:shadow-[0_32px_75px_-35px_rgba(15,23,42,0.7)]'
            )}
          >
            <button
              type="button"
              onClick={() => handleToggle(item.id)}
              className="flex w-full items-start justify-between gap-3 px-6 py-5 text-left"
            >
              <div>
                <p className="text-base font-semibold text-gray-900 sm:text-lg dark:text-white">{item.title}</p>
                {item.helperText && (
                  <p className="mt-1 text-sm text-gray-500 dark:text-white/75">{item.helperText}</p>
                )}
              </div>
              <span
                className={clsx(
                  'mt-1 flex h-9 w-9 items-center justify-center rounded-full bg-blue-50 text-blue-600 transition-transform duration-300 dark:bg-slate-800 dark:text-white',
                  isOpen && 'rotate-180'
                )}
              >
                <ChevronDown className="h-4 w-4" />
              </span>
            </button>
            <div
              className={clsx(
                'grid transition-all duration-300 ease-out',
                isOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
              )}
            >
              <div className="min-h-0 px-6 pb-6 text-sm text-gray-600 sm:text-base dark:text-white/80">
                <div className="rounded-2xl bg-white/70 p-5 shadow-inner shadow-blue-50/60 dark:bg-slate-900/60 dark:shadow-slate-900/40">
                  {item.description}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default Accordion;
