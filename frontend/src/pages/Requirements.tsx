import { useState } from "react";
import Layout from "@/components/Layout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ArrowRight, Minus, Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

interface RequirementItem {
  id: string;
  category: string;
  item: string;
  quantity: number;
  priority: "must-have" | "nice-to-have";
  targetPrice: string;
  quality: "basic" | "standard" | "premium";
}

export default function Requirements() {
  const navigate = useNavigate();
  const [items, setItems] = useState<RequirementItem[]>([
    {
      id: "1",
      category: "Chairs",
      item: "Office Chair - Task",
      quantity: 24,
      priority: "must-have",
      targetPrice: "200",
      quality: "standard",
    },
    {
      id: "2",
      category: "Desks",
      item: "Standing Desk",
      quantity: 10,
      priority: "must-have",
      targetPrice: "800",
      quality: "premium",
    },
    {
      id: "3",
      category: "Lighting",
      item: "LED Panel Light",
      quantity: 18,
      priority: "nice-to-have",
      targetPrice: "150",
      quality: "standard",
    },
  ]);

  const updateQuantity = (id: string, delta: number) => {
    setItems(
      items.map((item) =>
        item.id === id
          ? { ...item, quantity: Math.max(1, item.quantity + delta) }
          : item
      )
    );
  };

  const updateItem = (id: string, field: keyof RequirementItem, value: any) => {
    setItems(
      items.map((item) => (item.id === id ? { ...item, [field]: value } : item))
    );
  };

  const handleRunAnalysis = () => {
    toast.success("Running market analysis...");
    setTimeout(() => {
      navigate("/projects/1/suppliers");
    }, 1500);
  };

  const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
  const estimatedBudget = items.reduce(
    (sum, item) => sum + item.quantity * parseFloat(item.targetPrice || "0"),
    0
  );

  return (
    <Layout>
      <div className="container py-8 px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="font-heading text-4xl font-bold mb-2">
            Requirements & Prioritization
          </h1>
          <p className="text-muted-foreground">
            Adjust quantities, priorities, and constraints before running market analysis
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_350px]">
          {/* Main Table */}
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Item</TableHead>
                    <TableHead className="w-[140px]">Quantity</TableHead>
                    <TableHead className="w-[150px]">Priority</TableHead>
                    <TableHead className="w-[120px]">Target Price</TableHead>
                    <TableHead className="w-[140px]">Quality</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>
                        <div>
                          <p className="font-semibold">{item.item}</p>
                          <p className="text-sm text-muted-foreground">
                            {item.category}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button
                            size="icon"
                            variant="outline"
                            className="h-8 w-8"
                            onClick={() => updateQuantity(item.id, -1)}
                          >
                            <Minus className="h-3 w-3" />
                          </Button>
                          <Input
                            type="number"
                            value={item.quantity}
                            onChange={(e) =>
                              updateItem(
                                item.id,
                                "quantity",
                                parseInt(e.target.value) || 1
                              )
                            }
                            className="h-8 w-16 text-center"
                          />
                          <Button
                            size="icon"
                            variant="outline"
                            className="h-8 w-8"
                            onClick={() => updateQuantity(item.id, 1)}
                          >
                            <Plus className="h-3 w-3" />
                          </Button>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Select
                          value={item.priority}
                          onValueChange={(value) =>
                            updateItem(item.id, "priority", value)
                          }
                        >
                          <SelectTrigger className="h-8">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="must-have">Must-have</SelectItem>
                            <SelectItem value="nice-to-have">Nice-to-have</SelectItem>
                          </SelectContent>
                        </Select>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <span className="text-muted-foreground">$</span>
                          <Input
                            type="number"
                            value={item.targetPrice}
                            onChange={(e) =>
                              updateItem(item.id, "targetPrice", e.target.value)
                            }
                            className="h-8 w-20"
                          />
                        </div>
                      </TableCell>
                      <TableCell>
                        <Select
                          value={item.quality}
                          onValueChange={(value) =>
                            updateItem(item.id, "quality", value)
                          }
                        >
                          <SelectTrigger className="h-8">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="basic">Basic</SelectItem>
                            <SelectItem value="standard">Standard</SelectItem>
                            <SelectItem value="premium">Premium</SelectItem>
                          </SelectContent>
                        </Select>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </Card>

          {/* Summary Sidebar */}
          <div className="space-y-6">
            <Card className="p-6">
              <h3 className="font-heading text-lg font-bold mb-4">Summary</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">Total Items</p>
                  <p className="text-2xl font-bold">{totalItems}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Categories</p>
                  <p className="text-2xl font-bold">{items.length}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Est. Budget</p>
                  <p className="text-2xl font-bold">
                    ${estimatedBudget.toLocaleString()}
                  </p>
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="font-heading text-lg font-bold mb-4">Constraints</h3>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">
                    Budget Limit
                  </label>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">$</span>
                    <Input type="number" placeholder="Optional" />
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">
                    Timeline
                  </label>
                  <Select defaultValue="asap">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="asap">As soon as possible</SelectItem>
                      <SelectItem value="1month">Within 1 month</SelectItem>
                      <SelectItem value="3months">Within 3 months</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </Card>

            <Button
              size="lg"
              className="w-full gap-2"
              onClick={handleRunAnalysis}
            >
              Run Market Analysis
              <ArrowRight className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Bottom Navigation */}
        <div className="mt-8 flex justify-between">
          <Button variant="outline" onClick={() => navigate("/projects/1/upload")}>
            Back: Upload & Detection
          </Button>
        </div>
      </div>
    </Layout>
  );
}
