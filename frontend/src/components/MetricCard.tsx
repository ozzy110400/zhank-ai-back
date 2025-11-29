import React from 'react';

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  accent?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({ icon, label, value, accent }) => {
  return (
    <div className="flex items-center gap-4 px-6 py-3 bg-card/50 border border-border/20 rounded-xl">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center border ${
        accent 
          ? 'bg-primary/10 border-primary/40 text-primary' 
          : 'bg-card border-border/20 text-foreground/70'
      }`}>
        {icon}
      </div>
      <div>
        <div className="text-sm text-muted-foreground">{label}</div>
        <div className={`text-lg font-semibold ${accent ? 'text-primary' : 'text-foreground'}`}>
          {value}
        </div>
      </div>
    </div>
  );
};
