interface AgentCardProps {
  name: string;
  percentage: number;
  tags: string[];
  subtitle?: string;
  selected?: boolean;
  onClick?: () => void;
}

export const AgentCard = ({ name, percentage, tags, subtitle, selected = false, onClick }: AgentCardProps) => {
  const isHighPercentage = percentage >= 50;
  
  return (
    <div 
      className={`flex-1 p-4 bg-card border rounded-xl cursor-pointer transition-smooth ${
        selected 
          ? 'border-primary shadow-glow' 
          : 'border-border/20 hover:border-primary/30'
      }`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div>
            <h3 className="text-foreground font-semibold">{name}</h3>
            {subtitle && (
              <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>
            )}
          </div>
        </div>
        <span className={`text-lg font-bold ${isHighPercentage ? 'text-warning' : 'text-foreground/70'}`}>
          {percentage} %
        </span>
      </div>
      
      <div className="flex flex-wrap gap-2">
        {tags.map((tag, index) => (
          <span 
            key={index}
            className="px-2.5 py-1 bg-secondary border border-border/20 rounded-md text-xs text-muted-foreground"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
};
