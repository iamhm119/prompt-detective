import React from 'react';
import clsx from 'clsx';

interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
}

const PageContainer: React.FC<PageContainerProps> = ({ children, className }) => {
  return (
    <div className={clsx('space-y-12 pb-20', className)}>
      {children}
    </div>
  );
};

export default PageContainer;
