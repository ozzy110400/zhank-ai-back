import { Check } from 'lucide-react';

interface DetectionLabelProps {
  label: string;
  selected?: boolean;
  style?: React.CSSProperties;
  index?: number;
}

export const DetectionLabel = ({ label, selected = true, style, index = 0 }: DetectionLabelProps) => {
  return (
    <div 
      className="absolute flex items-center gap-1.5 px-3 py-1.5 bg-card/90 backdrop-blur-sm border border-primary/50 rounded-lg text-sm font-medium shadow-glow cursor-pointer hover:border-primary transition-smooth opacity-0 animate-pop-in animate-float"
      style={{
        ...style,
        animationDelay: `${index * 0.15}s, ${index * 0.15}s`,
        animationFillMode: 'forwards, none',
      }}
    >
      {selected && (
        <div className="w-4 h-4 bg-primary rounded flex items-center justify-center">
          <Check className="w-3 h-3 text-primary-foreground" />
        </div>
      )}
      <span className="text-foreground">{label}</span>
    </div>
  );
};
