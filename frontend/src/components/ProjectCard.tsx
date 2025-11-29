import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import StatusBadge from "./StatusBadge";
import { ArrowRight, Building2, Calendar } from "lucide-react";
import { Link } from "react-router-dom";

interface ProjectCardProps {
  id: string;
  name: string;
  thumbnail?: string;
  tags: string[];
  status: "detection" | "requirements" | "suppliers" | "summary" | "completed";
  progress: number;
  lastUpdated: string;
}

export default function ProjectCard({
  id,
  name,
  thumbnail,
  tags,
  status,
  progress,
  lastUpdated,
}: ProjectCardProps) {
  const getNextStepUrl = () => {
    switch (status) {
      case "detection":
        return `/projects/${id}/upload`;
      case "requirements":
        return `/projects/${id}/requirements`;
      case "suppliers":
        return `/projects/${id}/suppliers`;
      case "summary":
      case "completed":
        return `/projects/${id}/summary`;
      default:
        return `/projects/${id}/upload`;
    }
  };

  return (
    <Card className="group overflow-hidden transition-smooth hover:shadow-custom-md">
      <div className="aspect-video overflow-hidden bg-muted">
        {thumbnail ? (
          <img
            src={thumbnail}
            alt={name}
            className="h-full w-full object-cover transition-smooth group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <Building2 className="h-16 w-16 text-muted-foreground/30" />
          </div>
        )}
      </div>
      
      <CardHeader className="space-y-3">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-heading text-lg font-bold leading-tight">{name}</h3>
          <StatusBadge status={status} />
        </div>
        
        <div className="flex flex-wrap gap-1.5">
          {tags.map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-semibold text-foreground">{progress}%</span>
          </div>
          <Progress value={progress} className="h-1.5" />
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Calendar className="h-3.5 w-3.5" />
          <span>Updated {lastUpdated}</span>
        </div>
      </CardContent>

      <CardFooter className="flex gap-2">
        <Link to={getNextStepUrl()} className="flex-1">
          <Button className="w-full gap-2" size="sm">
            Continue
            <ArrowRight className="h-4 w-4" />
          </Button>
        </Link>
        {status === "completed" && (
          <Link to={`/projects/${id}/summary`}>
            <Button variant="outline" size="sm">
              View
            </Button>
          </Link>
        )}
      </CardFooter>
    </Card>
  );
}
