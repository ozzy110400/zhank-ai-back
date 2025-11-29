import { useState } from "react";
import Layout from "@/components/Layout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Star, Check, ArrowRight, TrendingUp } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";

interface Supplier {
  id: string;
  name: string;
  rating: number;
  pricePerUnit: number;
  totalPrice: number;
  deliveryDays: number;
  quality: string;
  tags: string[];
}

const mockSuppliers: Supplier[] = [
  {
    id: "1",
    name: "ErgoFlex Solutions",
    rating: 4.8,
    pricePerUnit: 189,
    totalPrice: 4536,
    deliveryDays: 7,
    quality: "Premium warranty",
    tags: ["Preferred", "Eco-certified"],
  },
  {
    id: "2",
    name: "Office Dynamics Pro",
    rating: 4.6,
    pricePerUnit: 195,
    totalPrice: 4680,
    deliveryDays: 5,
    quality: "2-year warranty",
    tags: ["Fast delivery"],
  },
  {
    id: "3",
    name: "WorkSpace Essentials",
    rating: 4.5,
    pricePerUnit: 175,
    totalPrice: 4200,
    deliveryDays: 10,
    quality: "Standard warranty",
    tags: ["Budget-friendly"],
  },
];

export default function Suppliers() {
  const navigate = useNavigate();
  const [selectedItem] = useState("Office Chair - Task");
  const [selectedSupplier, setSelectedSupplier] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState("best-match");

  const handleSelectSupplier = (supplierId: string) => {
    setSelectedSupplier(supplierId);
  };

  const handleNext = () => {
    navigate("/projects/1/summary");
  };

  return (
    <Layout>
      <div className="container py-8 px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="font-heading text-4xl font-bold mb-2">
            Suppliers & Matching
          </h1>
          <p className="text-muted-foreground">
            Compare suppliers and shortlist options for each item
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-[300px_1fr]">
          {/* Left Sidebar - Item Selector */}
          <Card className="p-6 h-fit">
            <h3 className="font-heading text-lg font-bold mb-4">Items</h3>
            <div className="space-y-2">
              <button
                className={cn(
                  "w-full rounded-lg border-2 p-4 text-left transition-smooth",
                  "border-primary bg-primary/5"
                )}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold">Office Chair - Task</p>
                    <p className="text-sm text-muted-foreground">Quantity: 24</p>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    5 suppliers
                  </Badge>
                </div>
              </button>

              <button className="w-full rounded-lg border-2 border-border p-4 text-left transition-smooth hover:border-primary/50">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold">Standing Desk</p>
                    <p className="text-sm text-muted-foreground">Quantity: 10</p>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    8 suppliers
                  </Badge>
                </div>
              </button>

              <button className="w-full rounded-lg border-2 border-border p-4 text-left transition-smooth hover:border-primary/50">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold">LED Panel Light</p>
                    <p className="text-sm text-muted-foreground">Quantity: 18</p>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    6 suppliers
                  </Badge>
                </div>
              </button>
            </div>
          </Card>

          {/* Right Content - Supplier List */}
          <div className="space-y-6">
            {/* Controls */}
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="font-heading text-2xl font-bold">{selectedItem}</h2>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-full sm:w-64">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="best-match">Best Match</SelectItem>
                  <SelectItem value="price-low">Price: Low to High</SelectItem>
                  <SelectItem value="price-high">Price: High to Low</SelectItem>
                  <SelectItem value="delivery">Fastest Delivery</SelectItem>
                  <SelectItem value="rating">Highest Rating</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Suppliers */}
            <div className="space-y-4">
              {mockSuppliers.map((supplier) => (
                <Card
                  key={supplier.id}
                  className={cn(
                    "p-6 transition-smooth",
                    selectedSupplier === supplier.id &&
                      "border-2 border-primary shadow-custom-md"
                  )}
                >
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                    <div className="flex-1 space-y-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-heading text-xl font-bold mb-1">
                            {supplier.name}
                          </h3>
                          <div className="flex items-center gap-2">
                            <div className="flex items-center gap-1">
                              <Star className="h-4 w-4 fill-accent text-accent" />
                              <span className="font-semibold">{supplier.rating}</span>
                            </div>
                            <span className="text-sm text-muted-foreground">
                              (248 reviews)
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-2">
                        {supplier.tags.map((tag) => (
                          <Badge key={tag} variant="secondary">
                            {tag}
                          </Badge>
                        ))}
                      </div>

                      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                        <div>
                          <p className="text-sm text-muted-foreground">Price/unit</p>
                          <p className="text-lg font-bold">
                            ${supplier.pricePerUnit}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Total</p>
                          <p className="text-lg font-bold text-primary">
                            ${supplier.totalPrice.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Delivery</p>
                          <p className="text-lg font-bold">
                            {supplier.deliveryDays} days
                          </p>
                        </div>
                      </div>

                      <p className="text-sm text-muted-foreground">
                        {supplier.quality}
                      </p>
                    </div>

                    <div className="flex gap-2 lg:flex-col">
                      <Button
                        variant={
                          selectedSupplier === supplier.id ? "default" : "outline"
                        }
                        className="flex-1 gap-2 lg:flex-none"
                        onClick={() => handleSelectSupplier(supplier.id)}
                      >
                        {selectedSupplier === supplier.id ? (
                          <>
                            <Check className="h-4 w-4" />
                            Selected
                          </>
                        ) : (
                          "Select"
                        )}
                      </Button>
                      <Button variant="ghost" className="flex-1 lg:flex-none">
                        Compare
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>

            {/* Best Match Badge */}
            <div className="rounded-lg border border-success/20 bg-success/5 p-4">
              <div className="flex items-start gap-3">
                <div className="rounded-full bg-success/10 p-2">
                  <TrendingUp className="h-5 w-5 text-success" />
                </div>
                <div>
                  <p className="font-semibold mb-1">AI Recommendation</p>
                  <p className="text-sm text-muted-foreground">
                    ErgoFlex Solutions offers the best balance of price, quality, and
                    delivery time for your requirements
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Navigation */}
        <div className="mt-8 flex justify-between">
          <Button
            variant="outline"
            onClick={() => navigate("/projects/1/requirements")}
          >
            Back: Requirements
          </Button>
          <Button
            size="lg"
            onClick={handleNext}
            disabled={!selectedSupplier}
            className="gap-2"
          >
            Next: Review Summary
            <ArrowRight className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </Layout>
  );
}
