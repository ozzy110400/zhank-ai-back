import { useState } from "react";
import Layout from "@/components/Layout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Upload as UploadIcon, Image as ImageIcon, Check, ArrowRight, Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

export default function Upload() {
  const navigate = useNavigate();
  const [photos, setPhotos] = useState<string[]>([]);
  const [selectedPhoto, setSelectedPhoto] = useState<number>(0);
  const [isDetecting, setIsDetecting] = useState(false);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      // Simulate file upload
      const newPhotos = Array.from(files).map((file) => URL.createObjectURL(file));
      setPhotos([...photos, ...newPhotos]);
      toast.success(`${files.length} photo(s) uploaded successfully`);
    }
  };

  const handleRunDetection = () => {
    setIsDetecting(true);
    // Simulate AI detection
    setTimeout(() => {
      setIsDetecting(false);
      toast.success("Detection completed! Found 24 items.");
    }, 2000);
  };

  const handleNext = () => {
    navigate("/projects/1/requirements");
  };

  return (
    <Layout>
      <div className="container py-8 px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="font-heading text-4xl font-bold mb-2">Upload & Detection</h1>
          <p className="text-muted-foreground">
            Upload photos of your space and let AI detect items automatically
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-[400px_1fr]">
          {/* Left Side - Upload */}
          <div className="space-y-6">
            <Card className="p-6">
              <h2 className="font-heading text-lg font-bold mb-4">Upload Photos</h2>
              
              <label className="group block cursor-pointer">
                <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-border bg-muted/30 p-8 transition-smooth hover:border-primary hover:bg-muted/50">
                  <div className="rounded-full bg-primary/10 p-4 mb-4 transition-smooth group-hover:bg-primary/20">
                    <UploadIcon className="h-8 w-8 text-primary" />
                  </div>
                  <p className="font-semibold text-center mb-1">
                    Drop files here or click to upload
                  </p>
                  <p className="text-sm text-muted-foreground text-center">
                    Upload multiple photos of your space
                  </p>
                </div>
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
            </Card>

            {photos.length > 0 && (
              <Card className="p-6">
                <h3 className="font-heading text-lg font-bold mb-4">
                  Uploaded Photos ({photos.length})
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {photos.map((photo, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedPhoto(index)}
                      className={`relative aspect-square overflow-hidden rounded-lg border-2 transition-smooth ${
                        selectedPhoto === index
                          ? "border-primary shadow-md"
                          : "border-border hover:border-primary/50"
                      }`}
                    >
                      <img
                        src={photo}
                        alt={`Upload ${index + 1}`}
                        className="h-full w-full object-cover"
                      />
                      {selectedPhoto === index && (
                        <div className="absolute top-2 right-2 rounded-full bg-primary p-1">
                          <Check className="h-3 w-3 text-primary-foreground" />
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </Card>
            )}
          </div>

          {/* Right Side - Preview & Detection */}
          <Card className="p-6">
            {photos.length === 0 ? (
              <div className="flex h-full min-h-[500px] flex-col items-center justify-center text-center">
                <div className="rounded-full bg-muted p-8 mb-6">
                  <ImageIcon className="h-16 w-16 text-muted-foreground/50" />
                </div>
                <h3 className="font-heading text-2xl font-bold mb-2">
                  No photos uploaded yet
                </h3>
                <p className="text-muted-foreground max-w-md">
                  Upload photos to get started with AI-powered object detection
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Photo Preview */}
                <div className="aspect-video overflow-hidden rounded-lg bg-muted">
                  <img
                    src={photos[selectedPhoto]}
                    alt="Selected preview"
                    className="h-full w-full object-contain"
                  />
                </div>

                {/* Detection Results */}
                <div className="rounded-lg border border-border bg-card p-6">
                  <div className="mb-4 flex items-center justify-between">
                    <h3 className="font-heading text-lg font-bold">
                      Detected Items
                    </h3>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleRunDetection}
                      disabled={isDetecting}
                    >
                      {isDetecting ? "Detecting..." : "Re-run Detection"}
                    </Button>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between rounded-lg bg-muted p-4">
                      <div>
                        <p className="font-semibold">Chairs</p>
                        <p className="text-sm text-muted-foreground">Office furniture</p>
                      </div>
                      <span className="rounded-full bg-primary px-3 py-1 text-sm font-bold text-primary-foreground">
                        24
                      </span>
                    </div>
                    <div className="flex items-center justify-between rounded-lg bg-muted p-4">
                      <div>
                        <p className="font-semibold">Desks</p>
                        <p className="text-sm text-muted-foreground">Workstations</p>
                      </div>
                      <span className="rounded-full bg-primary px-3 py-1 text-sm font-bold text-primary-foreground">
                        10
                      </span>
                    </div>
                    <div className="flex items-center justify-between rounded-lg bg-muted p-4">
                      <div>
                        <p className="font-semibold">Lighting</p>
                        <p className="text-sm text-muted-foreground">Ceiling fixtures</p>
                      </div>
                      <span className="rounded-full bg-primary px-3 py-1 text-sm font-bold text-primary-foreground">
                        18
                      </span>
                    </div>
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-4 w-full gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    Add Item Manually
                  </Button>
                </div>
              </div>
            )}
          </Card>
        </div>

        {/* Bottom Actions */}
        {photos.length > 0 && (
          <div className="mt-8 flex justify-between">
            <Button variant="outline" onClick={() => navigate("/projects")}>
              Back to Projects
            </Button>
            <Button size="lg" onClick={handleNext} className="gap-2">
              Next: Define Requirements
              <ArrowRight className="h-5 w-5" />
            </Button>
          </div>
        )}
      </div>
    </Layout>
  );
}
