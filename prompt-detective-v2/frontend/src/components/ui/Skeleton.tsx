import React from 'react';
import { twMerge } from 'tailwind-merge';

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  shimmer?: boolean;
}

const Skeleton: React.FC<SkeletonProps> = ({ className, shimmer = true, ...props }) => {
  return (
    <div
      className={twMerge(
        'relative overflow-hidden rounded-2xl bg-gradient-to-br from-gray-200/60 to-gray-100/80',
        className
      )}
      {...props}
    >
      {shimmer && (
        <span className="absolute inset-0 animate-shimmer bg-gradient-to-r from-transparent via-white/60 to-transparent" />
      )}
    </div>
  );
};

export default Skeleton;
