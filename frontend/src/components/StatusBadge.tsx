import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type ProjectStatus = "detection" | "requirements" | "suppliers" | "summary" | "completed";

interface StatusBadgeProps {
  status: ProjectStatus;
  className?: string;
}

const statusConfig = {
  detection: {
    label: "Detection",
    variant: "default" as const,
  },
  requirements: {
    label: "Requirements",
    variant: "secondary" as const,
  },
  suppliers: {
    label: "Suppliers",
    variant: "secondary" as const,
  },
  summary: {
    label: "Summary",
    variant: "secondary" as const,
  },
  completed: {
    label: "Completed",
    variant: "default" as const,
  },
};

export default function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status];
  
  return (
    <Badge 
      variant={config.variant}
      className={cn("font-medium", className)}
    >
      {config.label}
    </Badge>
  );
}
