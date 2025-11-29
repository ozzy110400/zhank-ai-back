import Layout from "@/components/Layout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { FileText, Download, Share2, Package, DollarSign, Truck } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Summary() {
  const navigate = useNavigate();

  return (
    <Layout>
      <div className="container py-8 px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="font-heading text-4xl font-bold mb-2">Project Summary</h1>
          <p className="text-muted-foreground">
            Review your shortlist before exporting or sending to procurement
          </p>
        </div>

        {/* Stats */}
        <div className="grid gap-6 mb-8 sm:grid-cols-2 lg:grid-cols-4">
          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="rounded-full bg-primary/10 p-3">
                <Package className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Items</p>
                <p className="text-2xl font-bold">52</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="rounded-full bg-accent/10 p-3">
                <FileText className="h-6 w-6 text-accent" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Categories</p>
                <p className="text-2xl font-bold">3</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="rounded-full bg-success/10 p-3">
                <DollarSign className="h-6 w-6 text-success" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Cost</p>
                <p className="text-2xl font-bold">$13,416</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="rounded-full bg-warning/10 p-3">
                <Truck className="h-6 w-6 text-warning" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Est. Delivery</p>
                <p className="text-2xl font-bold">5-10 days</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Shortlist Table */}
        <Card className="mb-8 overflow-hidden">
          <div className="border-b border-border p-6">
            <h2 className="font-heading text-2xl font-bold">Selected Suppliers</h2>
          </div>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Item</TableHead>
                  <TableHead>Quantity</TableHead>
                  <TableHead>Supplier</TableHead>
                  <TableHead>Total Price</TableHead>
                  <TableHead>Delivery</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell>
                    <div>
                      <p className="font-semibold">Office Chair - Task</p>
                      <p className="text-sm text-muted-foreground">Chairs</p>
                    </div>
                  </TableCell>
                  <TableCell>24</TableCell>
                  <TableCell>
                    <div>
                      <p className="font-semibold">ErgoFlex Solutions</p>
                      <p className="text-sm text-muted-foreground">★ 4.8</p>
                    </div>
                  </TableCell>
                  <TableCell className="font-semibold">$4,536</TableCell>
                  <TableCell>7 days</TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate("/projects/1/suppliers")}
                    >
                      Change
                    </Button>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>
                    <div>
                      <p className="font-semibold">Standing Desk</p>
                      <p className="text-sm text-muted-foreground">Desks</p>
                    </div>
                  </TableCell>
                  <TableCell>10</TableCell>
                  <TableCell>
                    <div>
                      <p className="font-semibold">Modern Workspace Co</p>
                      <p className="text-sm text-muted-foreground">★ 4.7</p>
                    </div>
                  </TableCell>
                  <TableCell className="font-semibold">$7,200</TableCell>
                  <TableCell>10 days</TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate("/projects/1/suppliers")}
                    >
                      Change
                    </Button>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>
                    <div>
                      <p className="font-semibold">LED Panel Light</p>
                      <p className="text-sm text-muted-foreground">Lighting</p>
                    </div>
                  </TableCell>
                  <TableCell>18</TableCell>
                  <TableCell>
                    <div>
                      <p className="font-semibold">BrightSpace Lighting</p>
                      <p className="text-sm text-muted-foreground">★ 4.6</p>
                    </div>
                  </TableCell>
                  <TableCell className="font-semibold">$1,680</TableCell>
                  <TableCell>5 days</TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate("/projects/1/suppliers")}
                    >
                      Change
                    </Button>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </Card>

        {/* Export Actions */}
        <Card className="p-6">
          <h3 className="font-heading text-xl font-bold mb-4">Export & Share</h3>
          <div className="flex flex-wrap gap-3">
            <Button className="gap-2">
              <Download className="h-4 w-4" />
              Export as PDF
            </Button>
            <Button variant="outline" className="gap-2">
              <FileText className="h-4 w-4" />
              Export as Excel
            </Button>
            <Button variant="outline" className="gap-2">
              <Share2 className="h-4 w-4" />
              Share Project
            </Button>
          </div>
        </Card>

        {/* Bottom Navigation */}
        <div className="mt-8 flex justify-between">
          <Button variant="outline" onClick={() => navigate("/projects/1/suppliers")}>
            Back: Suppliers
          </Button>
          <Button onClick={() => navigate("/projects")}>
            Return to Projects
          </Button>
        </div>
      </div>
    </Layout>
  );
}
