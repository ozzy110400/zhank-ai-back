import React from 'react';

interface ChipButtonProps {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}

export const ChipButton: React.FC<ChipButtonProps> = ({ active, onClick, children }) => {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
        active
          ? 'bg-primary text-primary-foreground shadow-glow'
          : 'bg-secondary text-secondary-foreground hover:bg-secondary/80 border border-border/20'
      }`}
    >
      {children}
    </button>
  );
};
