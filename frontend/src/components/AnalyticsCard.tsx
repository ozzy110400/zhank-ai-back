import React from 'react';

interface AnalyticsCardProps {
  title: string;
  children: React.ReactNode;
}

export const AnalyticsCard: React.FC<AnalyticsCardProps> = ({ title, children }) => {
  return (
    <div className="bg-card border border-border/20 rounded-2xl p-6">
      <h3 className="text-lg font-semibold text-foreground mb-2">{title}</h3>
      {children}
    </div>
  );
};
