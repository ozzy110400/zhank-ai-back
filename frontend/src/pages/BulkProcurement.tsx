import { useState, useRef } from 'react';
import { Zap, Camera, ArrowRight, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { DetectionLabel } from '@/components/DetectionLabel';
import { AgentCard } from '@/components/AgentCard';
import { InstructionsPanel } from '@/components/InstructionsPanel';
import officeImage from '@/assets/office-space.png';

const detectedItems = [
  { id: 1, label: 'Apple iMac', position: { top: '42%', left: '8%' } },
  { id: 2, label: 'JYSK Schreibtisch', position: { bottom: '8%', left: '8%' } },
  { id: 3, label: 'QAZQA Modern 1-circ..', position: { top: '18%', left: '50%' } },
  { id: 4, label: 'IKEA SKRUVSTA Chair', position: { top: '60%', right: '5%' } },
];

const agents = [
  {
    name: 'Filippo',
    percentage: 30,
    tags: ['Warm', 'Cooperative'],
  },
  {
    name: 'Diana',
    percentage: 70,
    tags: ['Aggressive', 'Price snob', 'Bargaining tactics'],
  },
  {
    name: 'Agatha',
    percentage: 50,
    tags: ['Competitive', 'Winner'],
  },
];

export default function BulkProcurement() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>('Filippo');
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [animationKey, setAnimationKey] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setUploadedImage(e.target?.result as string);
        setAnimationKey(prev => prev + 1); // Reset animation
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCameraClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="h-screen bg-background flex flex-col overflow-hidden">
      {/* Header */}
      <header className="h-16 px-6 flex items-center shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-card border border-primary/30 rounded-xl flex items-center justify-center animate-glow-pulse shrink-0">
            <Zap className="w-6 h-6 text-primary animate-icon-glow" />
          </div>
          <div className="w-[120px]">
            <span className="inline-block text-xl font-bold text-foreground overflow-hidden whitespace-nowrap animate-typewriter-loop">
              Zhank AI
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 px-6 pb-4 flex flex-col min-h-0">
        <div className="flex gap-6 flex-1 min-h-0">
          {/* Left Section */}
          <div className="flex-1 flex flex-col gap-4 min-h-0">
            {/* Bulk Procurement */}
            <div className="bg-card border border-border/20 rounded-2xl p-4 flex-1 flex flex-col min-h-0">
              <h2 className="text-primary font-semibold tracking-wide text-sm uppercase mb-3 shrink-0">
                Bulk Procurement
              </h2>
              
              {/* Image with Detection Labels */}
              <div className="relative rounded-xl overflow-hidden flex-1 min-h-0">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleImageUpload}
                  accept="image/*"
                  className="hidden"
                />
                <img 
                  src={uploadedImage || officeImage}
                  alt="Office space"
                  className="w-full h-full object-cover"
                />
                
                {/* Detection Labels */}
                {detectedItems.map((item, index) => (
                  <DetectionLabel 
                    key={`${item.id}-${animationKey}`}
                    label={item.label}
                    selected
                    style={item.position}
                    index={index}
                  />
                ))}
                
                {/* Camera/Upload Button */}
                <div className="absolute bottom-3 left-1/2 -translate-x-1/2">
                  <button 
                    onClick={handleCameraClick}
                    className="w-12 h-12 bg-card/80 backdrop-blur-sm border-2 border-primary/50 rounded-xl flex items-center justify-center hover:border-primary transition-smooth shadow-glow group"
                  >
                    <Upload className="w-6 h-6 text-foreground/80 group-hover:text-primary transition-smooth" />
                  </button>
                </div>
              </div>
            </div>

            {/* Agents */}
            <div className="shrink-0">
              <h2 className="text-primary font-semibold tracking-wide text-sm uppercase mb-3">
                Agents
              </h2>
              
              <div className="flex gap-3">
                {agents.map((agent, index) => (
                  <AgentCard 
                    key={index}
                    name={agent.name}
                    percentage={agent.percentage}
                    tags={agent.tags}
                    selected={selectedAgent === agent.name}
                    onClick={() => setSelectedAgent(agent.name)}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Right Section - Instructions */}
          <div className="w-[380px] shrink-0">
            <InstructionsPanel />
          </div>
        </div>

        {/* Further Button */}
        <div className="flex justify-end mt-4 shrink-0">
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-6 py-2.5 gap-2">
            Further
            <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
