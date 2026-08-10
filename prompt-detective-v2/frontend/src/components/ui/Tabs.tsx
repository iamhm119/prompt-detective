import React, { useState } from 'react';
import clsx from 'clsx';

export interface TabItem {
  value: string;
  label: string;
  icon?: React.ReactNode;
  badge?: React.ReactNode;
  content: React.ReactNode;
}

export interface TabsProps {
  items: TabItem[];
  defaultValue?: string;
  onChange?: (value: string) => void;
  className?: string;
  orientation?: 'horizontal' | 'vertical';
}

const Tabs: React.FC<TabsProps> = ({
  items,
  defaultValue,
  onChange,
  className,
  orientation = 'horizontal',
}) => {
  const [active, setActive] = useState(defaultValue ?? items[0]?.value);

  const handleChange = (value: string) => {
    setActive(value);
    onChange?.(value);
  };

  const isVertical = orientation === 'vertical';

  const activeItem = items.find((item) => item.value === active) ?? items[0];

  return (
    <div className={clsx('flex gap-6', isVertical && 'md:flex-row', className)}>
      <div
        className={clsx(
          'flex gap-2 rounded-2xl bg-white/80 p-2 shadow-[0_12px_35px_-18px_rgba(99,102,241,0.45)] backdrop-blur-md',
          isVertical ? 'flex-col w-56' : 'flex-wrap'
        )}
      >
        {items.map((item) => {
          const isActive = item.value === active;
          return (
            <button
              key={item.value}
              type="button"
              onClick={() => handleChange(item.value)}
              className={clsx(
                'relative flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition-all duration-300',
                isActive
                  ? 'bg-gradient-to-r from-blue-600 via-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-200'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100/60'
              )}
            >
              {item.icon && <span className="text-lg">{item.icon}</span>}
              <span>{item.label}</span>
              {item.badge && <span>{item.badge}</span>}
            </button>
          );
        })}
      </div>

      <div className="flex-1">
        <div className="rounded-3xl bg-white/90 p-6 shadow-[0_30px_70px_-35px_rgba(79,70,229,0.55)] backdrop-blur-xl">
          {activeItem?.content}
        </div>
      </div>
    </div>
  );
};

export default Tabs;
