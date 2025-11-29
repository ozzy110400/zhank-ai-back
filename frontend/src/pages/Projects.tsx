import { useState } from "react";
import Layout from "@/components/Layout";
import ProjectCard from "@/components/ProjectCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, Search } from "lucide-react";
import { Link } from "react-router-dom";

// Mock data
const mockProjects = [
  {
    id: "1",
    name: "HQ – Open Space 4th Floor",
    tags: ["Office", "Open Space"],
    status: "requirements" as const,
    progress: 45,
    lastUpdated: "2 hours ago",
  },
  {
    id: "2",
    name: "Building A – Conference Rooms",
    tags: ["Meeting Room", "Corporate"],
    status: "suppliers" as const,
    progress: 70,
    lastUpdated: "Yesterday",
  },
  {
    id: "3",
    name: "Warehouse 2 – Storage Area",
    tags: ["Warehouse", "Industrial"],
    status: "completed" as const,
    progress: 100,
    lastUpdated: "3 days ago",
  },
  {
    id: "4",
    name: "Executive Suite Renovation",
    tags: ["Office", "Premium"],
    status: "detection" as const,
    progress: 20,
    lastUpdated: "1 week ago",
  },
];

export default function Projects() {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const filteredProjects = mockProjects.filter((project) => {
    const matchesSearch = project.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || project.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <Layout>
      <div className="container py-8 px-4">
        {/* Header */}
        <div className="mb-8 space-y-4">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="font-heading text-4xl font-bold mb-2">Projects</h1>
              <p className="text-muted-foreground">
                Manage your procurement projects and track progress
              </p>
            </div>
            <Link to="/projects/new/upload">
              <Button size="lg" className="gap-2">
                <Plus className="h-5 w-5" />
                New Project
              </Button>
            </Link>
          </div>

          {/* Filters */}
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by project name or tags..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="detection">Detection</SelectItem>
                <SelectItem value="requirements">Requirements</SelectItem>
                <SelectItem value="suppliers">Suppliers</SelectItem>
                <SelectItem value="summary">Summary</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Projects Grid */}
        {filteredProjects.length > 0 ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredProjects.map((project) => (
              <ProjectCard key={project.id} {...project} />
            ))}
          </div>
        ) : (
          <div className="flex min-h-[400px] flex-col items-center justify-center text-center">
            <div className="rounded-full bg-muted p-6 mb-4">
              <Search className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="font-heading text-xl font-semibold mb-2">No projects found</h3>
            <p className="text-muted-foreground mb-6">
              Try adjusting your search or filters
            </p>
            <Button onClick={() => { setSearchQuery(""); setStatusFilter("all"); }}>
              Clear Filters
            </Button>
          </div>
        )}
      </div>
    </Layout>
  );
}
